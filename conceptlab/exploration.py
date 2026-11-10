"""Finite attribute exploration with an explicitly supplied exact table expert."""
from copy import deepcopy
from .core import validate


def validate_exploration(data):
    if type(data) is not dict or set(data) != {'context', 'initial_objects'}:
        raise ValueError('expected exactly context and initial_objects')
    m, rows = validate(data['context'])
    if m > 5:
        raise ValueError('exploration permits at most five attributes')
    ids = data['initial_objects']
    if type(ids) is not list or any(type(i) is not int or not 0 <= i < len(rows) for i in ids) or len(set(ids)) != len(ids):
        raise ValueError('initial_objects must be unique expert row indices')
    return m, rows, sorted(ids), deepcopy(data)


def explore(data):
    m, rows, known, data = validate_exploration(data)
    full = (1 << m) - 1
    basis = []
    events = []
    current = 0

    def table_closure(premise, ids):
        support = [i for i in ids if rows[i] & premise == premise]
        value = full
        for i in support:
            value &= rows[i]
        return value, support

    def knowledge_closure(seed):
        result = seed
        rounds = []
        while True:
            before = result
            firing = []
            for i, rule in enumerate(basis):
                if rule['premise_mask'] & before == rule['premise_mask']:
                    firing.append(i)
                    result |= rule['conclusion_mask']
            rounds.append({'before': before, 'firing': firing,
                           'added': result & ~before, 'after': result})
            if result == before:
                return result, rounds

    while True:
        observed, support = table_closure(current, known)
        domain, domain_support = table_closure(current, range(len(rows)))
        before_known = list(known)
        before_basis = deepcopy(basis)
        question = observed != current
        counterexamples = [i for i, row in enumerate(rows)
                           if row & current == current and row & observed != observed] if question else []
        response = ('reject' if counterexamples else 'accept') if question else 'closed'
        selected = counterexamples[0] if counterexamples else None
        accepted_id = None
        attempts = []
        successor = None
        if response == 'reject':
            assert selected not in known
            known = sorted(known + [selected])
            # A correct expert cannot retract an earlier accepted implication.
            assert all(rows[selected] & r['premise_mask'] != r['premise_mask'] or
                       rows[selected] & r['conclusion_mask'] == r['conclusion_mask'] for r in basis)
        else:
            if response == 'accept':
                accepted_id = len(basis)
                basis.append({'id': accepted_id, 'premise_mask': current,
                              'conclusion_mask': observed & ~current,
                              'closure_mask': observed})
            for pivot in reversed(range(m)):
                if current & (1 << pivot):
                    continue
                lower = (1 << pivot) - 1
                seed = (current & lower) | (1 << pivot)
                candidate, derivation = knowledge_closure(seed)
                diff = [a for a in range(pivot) if bool(candidate & (1 << a)) != bool(current & (1 << a))]
                allowed = not diff
                attempts.append({'pivot': pivot, 'seed_mask': seed,
                                 'closure_mask': candidate, 'derivation': derivation,
                                 'earlier_disagreements': diff, 'accepted': allowed})
                if allowed:
                    successor = candidate
                    break
        events.append({'id': len(events), 'premise_mask': current,
                       'known_before': before_known, 'basis_before': before_basis,
                       'observed_closure_mask': observed,
                       'observed_support': support,
                       'domain_closure_mask': domain, 'domain_support': domain_support,
                       'question': question, 'conclusion_mask': observed & ~current,
                       'response': response, 'counterexample_ids': counterexamples,
                       'selected_counterexample': selected,
                       'selected_attributes_mask': rows[selected] if selected is not None else None,
                       'accepted_rule_id': accepted_id, 'known_after': list(known),
                       'basis_after': deepcopy(basis), 'next_attempts': attempts,
                       'next_premise_mask': current if response == 'reject' else successor})
        assert len(events) <= (1 << m) + len(rows)
        if response == 'reject':
            continue
        if successor is None:
            break
        current = successor
    audit = []
    for premise in range(1 << m):
        k, derivation = knowledge_closure(premise)
        d, ds = table_closure(premise, range(len(rows)))
        o, os = table_closure(premise, known)
        assert k == d == o
        audit.append({'premise_mask': premise, 'knowledge_closure_mask': k,
                      'domain_closure_mask': d, 'observed_closure_mask': o,
                      'domain_support': ds, 'observed_support': os,
                      'derivation': derivation,
                      'missing_attribute_counterexamples': [
                          {'attribute': a, 'object_ids': [i for i in ds if not rows[i] & (1 << a)]}
                          for a in range(m) if not d & (1 << a)]})
    return {'schema': 'conceptlab-exploration-v1', 'input': data,
            'events': events, 'basis': basis, 'final_objects': known,
            'unseen_objects': [i for i in range(len(rows)) if i not in known],
            'closure_audit': audit, 'complete': True,
            'question_count': sum(e['question'] for e in events),
            'accept_count': sum(e['response'] == 'accept' for e in events),
            'reject_count': sum(e['response'] == 'reject' for e in events)}
