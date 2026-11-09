"""Exact finite formal contexts. Original exhaustive educational implementation."""


def validate(data):
    if not isinstance(data, dict) or set(data) != {'attributes', 'objects'}:
        raise ValueError('expected exactly attributes and objects')
    m, rows = data['attributes'], data['objects']
    if type(m) is not int or not 0 <= m <= 6:
        raise ValueError('attributes must be an integer in 0..6')
    if not isinstance(rows, list) or len(rows) > 8:
        raise ValueError('objects must be an array of at most eight attribute arrays')
    masks = []
    for row in rows:
        if not isinstance(row, list) or any(type(a) is not int or not 0 <= a < m for a in row):
            raise ValueError('every object must list valid integer attribute indices')
        if len(set(row)) != len(row):
            raise ValueError('duplicate attribute in object')
        masks.append(sum(1 << a for a in row))
    return m, masks


def audit(data):
    m, rows = validate(data)
    n, all_attrs = len(rows), (1 << m) - 1
    def extent(b):
        return sum(1 << g for g, row in enumerate(rows) if row & b == b)
    def intent(a):
        result = all_attrs
        for g, row in enumerate(rows):
            if a >> g & 1:
                result &= row
        return result
    def closure(b):
        return intent(extent(b))
    subsets = []
    for b in range(1 << m):
        e, c = extent(b), closure(b)
        subsets.append({'mask': b, 'extent_mask': e, 'closure_mask': c,
                        'closed': b == c, 'support_count': e.bit_count(),
                        'support_denominator': n,
                        'missing_attribute_counterexamples': [
                            {'attribute': a, 'objects': [g for g, row in enumerate(rows)
                                                       if e >> g & 1 and not row >> a & 1]}
                            for a in range(m) if not c >> a & 1]})
    intents = [x['mask'] for x in subsets if x['closed']]
    concepts = [{'id': i, 'intent_mask': b, 'extent_mask': extent(b)} for i, b in enumerate(intents)]
    by_intent = {c['intent_mask']: c['id'] for c in concepts}
    def below(x, y):
        return x['extent_mask'] & y['extent_mask'] == x['extent_mask']
    covers = [{'lower': x['id'], 'upper': y['id']} for x in concepts for y in concepts
              if x != y and below(x, y) and not any(
                  z != x and z != y and below(x, z) and below(z, y) for z in concepts)]
    operations = []
    for x in concepts:
        for y in concepts:
            meet_intent = closure(x['intent_mask'] | y['intent_mask'])
            join_intent = x['intent_mask'] & y['intent_mask']
            operations.append({'left': x['id'], 'right': y['id'],
                               'meet': by_intent[meet_intent], 'join': by_intent[join_intent]})
    pseudo = []
    pseudo_tests = []
    for b in sorted(range(1 << m), key=lambda x: (x.bit_count(), x)):
        prior = [q for q in pseudo if q & b == q]
        blockers = [q for q in prior if closure(q) & b != closure(q)]
        accepted = closure(b) != b and not blockers
        pseudo_tests.append({'mask': b, 'closed': closure(b) == b,
                             'prior_pseudo_subsets': prior, 'blocking_pseudo_subsets': blockers,
                             'pseudo_intent': accepted})
        if accepted:
            pseudo.append(b)
    basis = [{'id': i, 'premise_mask': p, 'conclusion_mask': closure(p) & ~p,
              'closure_mask': closure(p)} for i, p in enumerate(pseudo)]
    traces = []
    for start in range(1 << m):
        current, steps = start, []
        while True:
            fired = None
            for rule in basis:
                p, q = rule['premise_mask'], rule['conclusion_mask']
                if p & current == p and q & current != q:
                    fired = rule
                    break
            if fired is None:
                break
            after = current | fired['conclusion_mask']
            steps.append({'rule': fired['id'], 'before_mask': current, 'after_mask': after,
                          'added_mask': after & ~current})
            current = after
        assert current == closure(start)
        traces.append({'start_mask': start, 'steps': steps, 'final_mask': current})
    object_subsets = [{'mask': a, 'intent_mask': intent(a),
                       'closure_mask': extent(intent(a)),
                       'closed': a == extent(intent(a))} for a in range(1 << n)]
    irredundancy = []
    for removed in basis:
        current = removed['premise_mask']
        steps = []
        while True:
            applicable = [r for r in basis if r != removed
                          and r['premise_mask'] & current == r['premise_mask']
                          and r['conclusion_mask'] & current != r['conclusion_mask']]
            if not applicable:
                break
            rule = applicable[0]
            after = current | rule['conclusion_mask']
            steps.append({'rule': rule['id'], 'before_mask': current, 'after_mask': after})
            current = after
        assert current & removed['conclusion_mask'] != removed['conclusion_mask']
        irredundancy.append({'removed_rule': removed['id'], 'start_mask': removed['premise_mask'],
                             'steps': steps, 'model_mask': current,
                             'missing_conclusion_mask': removed['conclusion_mask'] & ~current})
    # NextClosure enumerates closed intents in lectic order (attribute 0 first).
    current, sequence, attempts = closure(0), [closure(0)], []
    while current != all_attrs:
        found = False
        for i in range(m - 1, -1, -1):
            if current >> i & 1:
                continue
            lower = (1 << i) - 1
            seed = (current & lower) | (1 << i)
            candidate = closure(seed)
            discrepancy = (candidate ^ current) & lower
            accepted = not discrepancy
            attempts.append({'from_mask': current, 'attribute': i, 'seed_mask': seed,
                             'closure_mask': candidate, 'earlier_difference_mask': discrepancy,
                             'accepted': accepted})
            if accepted:
                current = candidate
                sequence.append(current)
                found = True
                break
        assert found
    assert set(sequence) == set(intents) and len(sequence) == len(intents)
    return {'schema': 'conceptlab.audit.v1',
            'context': {'attributes': m, 'objects': [sorted(row) for row in data['objects']]},
            'attribute_subsets': subsets, 'object_subsets': object_subsets,
            'basis_irredundancy': irredundancy, 'concepts': concepts, 'covers': covers,
            'lattice_operations': operations, 'pseudo_intent_tests': pseudo_tests,
            'canonical_basis': basis, 'closure_traces': traces,
            'next_closure': {'intents': sequence, 'attempts': attempts}}
