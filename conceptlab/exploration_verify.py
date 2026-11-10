"""Set/model-intersection exploration verifier, independent of the generator."""
import json
from copy import deepcopy
from .exploration import validate_exploration


def verify_exploration(report):
    if type(report) is not dict or 'input' not in report:
        raise ValueError('expected exploration evidence')
    m, masks, known, data = validate_exploration(report['input'])
    universe = set(range(m))
    subsets = [{a for a in universe if mask & (1 << a)} for mask in range(1 << m)]
    rows = [set(subsets[mask]) for mask in masks]
    mask = lambda xs: sum(1 << a for a in xs)
    lectic = lambda xs: tuple(int(a in xs) for a in range(m))
    basis = []
    events = []

    def context_closure(premise, ids):
        support = [i for i in ids if premise <= rows[i]]
        common = set(universe)
        for i in support:
            common.intersection_update(rows[i])
        return common, support

    def respects(value, rule):
        return not subsets[rule['premise_mask']] <= value or subsets[rule['conclusion_mask']] <= value

    def theory_closure(seed):
        models = [s for s in subsets if seed <= s and all(respects(s, r) for r in basis)]
        result = set(universe)
        for s in models:
            result &= s
        # Reconstruct display rounds separately from model-intersection result.
        value = set(seed)
        rounds = []
        while True:
            before = set(value)
            firing = [i for i, r in enumerate(basis) if subsets[r['premise_mask']] <= before]
            for i in firing:
                value |= subsets[basis[i]['conclusion_mask']]
            rounds.append({'before': mask(before), 'firing': firing,
                           'added': mask(value - before), 'after': mask(value)})
            if value == before:
                break
        if value != result:
            raise ValueError('display derivation differs from theory-model intersection')
        return result, rounds

    premise = set()
    while True:
        observed, support = context_closure(premise, known)
        domain, ds = context_closure(premise, range(len(rows)))
        before_known, before_basis = list(known), deepcopy(basis)
        question = observed != premise
        counters = [i for i, row in enumerate(rows) if premise <= row and not observed <= row] if question else []
        response = ('reject' if counters else 'accept') if question else 'closed'
        chosen = min(counters) if counters else None
        accepted_id = None
        attempts = []
        successor = None
        if response == 'reject':
            if chosen in known or not all(respects(rows[chosen], r) for r in basis):
                raise ValueError('invalid expert counterexample')
            known = sorted(known + [chosen])
        else:
            if response == 'accept':
                accepted_id = len(basis)
                basis.append({'id': accepted_id, 'premise_mask': mask(premise),
                              'conclusion_mask': mask(observed - premise),
                              'closure_mask': mask(observed)})
            # Independently find the next theory-closed set by brute lectic sort.
            larger = sorted([s for s in subsets if lectic(s) > lectic(premise) and
                             all(respects(s, r) for r in basis)], key=lectic)
            brute_next = larger[0] if larger else None
            for pivot in range(m - 1, -1, -1):
                if pivot in premise:
                    continue
                seed = {a for a in premise if a < pivot} | {pivot}
                candidate, derivation = theory_closure(seed)
                disagreements = [a for a in range(pivot) if (a in candidate) != (a in premise)]
                okay = not disagreements
                attempts.append({'pivot': pivot, 'seed_mask': mask(seed),
                                 'closure_mask': mask(candidate), 'derivation': derivation,
                                 'earlier_disagreements': disagreements, 'accepted': okay})
                if okay:
                    successor = candidate
                    break
            if successor != brute_next:
                raise ValueError('lectic pivot does not match exhaustive successor')
        events.append({'id': len(events), 'premise_mask': mask(premise),
                       'known_before': before_known, 'basis_before': before_basis,
                       'observed_closure_mask': mask(observed), 'observed_support': support,
                       'domain_closure_mask': mask(domain), 'domain_support': ds,
                       'question': question, 'conclusion_mask': mask(observed - premise),
                       'response': response, 'counterexample_ids': counters,
                       'selected_counterexample': chosen,
                       'selected_attributes_mask': mask(rows[chosen]) if chosen is not None else None,
                       'accepted_rule_id': accepted_id, 'known_after': list(known),
                       'basis_after': deepcopy(basis), 'next_attempts': attempts,
                       'next_premise_mask': mask(premise) if response == 'reject' else mask(successor) if successor is not None else None})
        if len(events) > (1 << m) + len(rows):
            raise ValueError('exploration exceeds finite progress bound')
        if response == 'reject':
            continue
        if successor is None:
            break
        premise = successor
    # A second characterization checks the final basis independently: recursive
    # pseudo-intents in inclusion order, not the exploration question procedure.
    pseudo = []
    for value in sorted(subsets, key=lambda s: (len(s), mask(s))):
        closed, _ = context_closure(value, range(len(rows)))
        if value != closed and all(context_closure(q, range(len(rows)))[0] <= value
                                   for q in pseudo if q < value):
            pseudo.append(value)
    expected_rules = {(mask(p), mask(context_closure(p, range(len(rows)))[0] - p)) for p in pseudo}
    actual_rules = {(r['premise_mask'], r['conclusion_mask']) for r in basis}
    if actual_rules != expected_rules:
        raise ValueError('accepted theory is not the finite canonical basis')
    audit = []
    for value in subsets:
        learned, derivation = theory_closure(value)
        domain, ds = context_closure(value, range(len(rows)))
        observed, os = context_closure(value, known)
        if not learned == domain == observed:
            raise ValueError('final closure theory incomplete')
        audit.append({'premise_mask': mask(value), 'knowledge_closure_mask': mask(learned),
                      'domain_closure_mask': mask(domain), 'observed_closure_mask': mask(observed),
                      'domain_support': ds, 'observed_support': os, 'derivation': derivation,
                      'missing_attribute_counterexamples': [
                          {'attribute': a, 'object_ids': [i for i in ds if a not in rows[i]]}
                          for a in range(m) if a not in domain]})
    expected = {'schema': 'conceptlab-exploration-v1', 'input': data,
                'events': events, 'basis': basis, 'final_objects': known,
                'unseen_objects': [i for i in range(len(rows)) if i not in known],
                'closure_audit': audit, 'complete': True,
                'question_count': sum(e['question'] for e in events),
                'accept_count': sum(e['response'] == 'accept' for e in events),
                'reject_count': sum(e['response'] == 'reject' for e in events)}
    canonical = lambda x: json.dumps(x, sort_keys=True, separators=(',', ':'), allow_nan=False)
    if canonical(report) != canonical(expected):
        raise ValueError('exploration evidence differs from independent reconstruction')
    return True
