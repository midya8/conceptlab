"""Bounded incomplete-context completion semantics. No completion probabilities."""
from functools import cmp_to_key


def validate(data):
    if not isinstance(data, dict) or set(data) != {'attributes', 'objects', 'goals'}:
        raise ValueError('expected exactly attributes, objects and goals')
    m, rows, goals = data['attributes'], data['objects'], data['goals']
    if type(m) is not int or not 0 <= m <= 4:
        raise ValueError('attributes must be an integer in 0..4')
    if not isinstance(rows, list) or len(rows) > 4:
        raise ValueError('objects must be an array of at most four matrix rows')
    if any(not isinstance(row, list) or len(row) != m or any(v is not None and (type(v) is not int or v not in (0, 1)) for v in row) for row in rows):
        raise ValueError('each matrix row must contain attributes entries of 0, 1 or null')
    unknown = [(g, a) for g, row in enumerate(rows) for a, v in enumerate(row) if v is None]
    if len(unknown) > 6:
        raise ValueError('at most six unknown cells')
    if not isinstance(goals, list) or len(goals) > 4:
        raise ValueError('goals must be an array of at most four implications')
    masks = []
    for goal in goals:
        if not isinstance(goal, dict) or set(goal) != {'premise', 'conclusion'}:
            raise ValueError('each goal must have exactly premise and conclusion')
        pair = []
        for k in ('premise', 'conclusion'):
            v = goal[k]
            if not isinstance(v, list) or any(type(a) is not int or not 0 <= a < m for a in v) or len(set(v)) != len(v):
                raise ValueError('goal attributes must be unique valid integer indices')
            pair.append(sum(1 << a for a in v))
        masks.append(pair)
    return m, rows, unknown, masks


def audit_partial(data):
    m, rows, unknown, goals = validate(data)
    size, n = 1 << m, len(rows)
    completions = []
    for c in range(1 << len(unknown)):
        matrix = [list(row) for row in rows]
        for i, (g, a) in enumerate(unknown):
            matrix[g][a] = (c >> i) & 1
        obj = [sum(v << a for a, v in enumerate(row)) for row in matrix]
        subsets = []
        for p in range(size):
            support = [g for g, row in enumerate(obj) if row & p == p]
            closure = size - 1
            for g in support:
                closure &= obj[g]
            subsets.append({'mask': p, 'support_objects': support, 'closure_mask': closure})
        completions.append({'id': c, 'object_masks': obj, 'attribute_subsets': subsets})
    queries = []
    def cmp(a, b):
        return (a[0] * b[1] > b[0] * a[1]) - (a[0] * b[1] < b[0] * a[1])
    for p in range(size):
        for q in range(size):
            valid, invalid, undefined, fractions, witnesses = [], [], [], [], []
            supports = []
            for c in completions:
                support = c['attribute_subsets'][p]['support_objects']
                bad = [g for g in support if c['object_masks'][g] & q != q]
                witnesses.append({'completion': c['id'], 'counterexample_objects': bad})
                (invalid if bad else valid).append(c['id'])
                supports.append(len(support))
                if support:
                    fractions.append([len(support) - len(bad), len(support), c['id']])
                else:
                    undefined.append(c['id'])
            ordered = sorted(fractions, key=cmp_to_key(cmp))
            bounds = []
            for extreme in ([ordered[0], ordered[-1]] if ordered else []):
                representative = next(x for x in fractions if cmp(x, extreme) == 0)
                num, den = representative[:2]
                bounds.append({'numerator': num, 'denominator': den,
                               'completions': [x[2] for x in fractions if x[0] * den == num * x[1]]})
            queries.append({'id': p * size + q, 'premise_mask': p, 'conclusion_mask': q,
                            'certain': not invalid, 'possible': bool(valid),
                            'status': 'certain' if not invalid else 'contingent' if valid else 'impossible',
                            'valid_completions': valid, 'invalid_completions': invalid,
                            'counterexamples': witnesses,
                            'support_count_min': min(supports), 'support_count_max': max(supports),
                            'confidence_undefined_completions': undefined,
                            'confidence_min': bounds[0] if bounds else None,
                            'confidence_max': bounds[-1] if bounds else None})
    goal_ids = [p * size + q for p, q in goals]
    goal_sets = []
    for mask in range(1 << len(goals)):
        selected = [i for i in range(len(goals)) if mask >> i & 1]
        valid = [c['id'] for c in completions if all(c['id'] in queries[goal_ids[i]]['valid_completions'] for i in selected)]
        goal_sets.append({'mask': mask, 'goals': selected, 'valid_completions': valid,
                          'possible': bool(valid), 'certain': len(valid) == len(completions)})
    conflicts = []
    for s in goal_sets:
        if not s['possible'] and all(goal_sets[s['mask'] & ~(1 << i)]['possible'] for i in s['goals']):
            conflicts.append({'mask': s['mask'], 'deletion_witnesses': [
                {'removed_goal': i, 'completions': goal_sets[s['mask'] & ~(1 << i)]['valid_completions']}
                for i in s['goals']]})
    return {'schema': 'conceptlab.partial.v1',
            'context': {'attributes': m, 'objects': [list(row) for row in rows],
                        'goals': [{'premise': sorted(g['premise']), 'conclusion': sorted(g['conclusion'])} for g in data['goals']]},
            'unknown_cells': [{'object': g, 'attribute': a, 'bit': i} for i, (g, a) in enumerate(unknown)],
            'completions': completions, 'queries': queries, 'goal_query_ids': goal_ids,
            'goal_subsets': goal_sets, 'minimal_impossible_goal_sets': conflicts}
