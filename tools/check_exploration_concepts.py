"""Optional external closure cross-check. Install concepts==0.9.2 separately.
This checks domain/observed closures, not the exploration scheduling algorithm.
Empty dimensions are explicitly excluded because Context requires nonempty axes.
"""
from functools import lru_cache
import itertools
import json
from pathlib import Path
import random
import concepts
from conceptlab.exploration import explore
from conceptlab.exploration_verify import verify_exploration


@lru_cache(maxsize=None)
def external_context(m, rows, ids):
    return concepts.Context(['g' + str(i) for i in ids],
                            ['a' + str(a) for a in range(m)],
                            [tuple(a in rows[i] for a in range(m)) for i in ids])


@lru_cache(maxsize=None)
def reference_cached(m, rows, ids, premise):
    c = external_context(m, rows, ids)
    support = c.extension(['a' + str(a) for a in range(m) if premise >> a & 1])
    return sum(1 << int(a[1:]) for a in c.intension(support)), [int(g[1:]) for g in support]


def check(data):
    global requests, closures, skipped_empty
    report = explore(data)
    verify_exploration(report)
    m = data['context']['attributes']
    rows = data['context']['objects']
    requests += 1
    if not m or not rows:
        skipped_empty += 1
        return
    def reference(ids, premise):
        return reference_cached(m, tuple(tuple(r) for r in rows), tuple(ids), premise)
    for a in report['closure_audit']:
        got, support = reference(list(range(len(rows))), a['premise_mask'])
        assert got == a['domain_closure_mask'] and support == a['domain_support']
        closures += 1
        if report['final_objects']:
            got, support = reference(report['final_objects'], a['premise_mask'])
            assert got == a['observed_closure_mask'] and support == a['observed_support']
            closures += 1
    for e in report['events']:
        if e['known_before']:
            got, support = reference(e['known_before'], e['premise_mask'])
            assert got == e['observed_closure_mask'] and support == e['observed_support']
            closures += 1


requests = closures = skipped_empty = 0
for m in range(4):
    for family in range(1 << (1 << m)):
        rows = [[a for a in range(m) if r >> a & 1] for r in range(1 << m) if family >> r & 1]
        for initial in range(1 << len(rows)):
            check({'context': {'attributes': m, 'objects': rows},
                   'initial_objects': [i for i in range(len(rows)) if initial >> i & 1]})
rng = random.Random(6481)
for _ in range(300):
    m = rng.randrange(6)
    rows = [[a for a in range(m) if rng.randrange(2)] for _ in range(rng.randrange(9))]
    check({'context': {'attributes': m, 'objects': rows},
           'initial_objects': [i for i in range(len(rows)) if rng.randrange(2)]})
for c in json.loads((Path(__file__).resolve().parents[1] / 'docs/exploration-controls.json').read_text()):
    check(c['input'])
print(json.dumps({'reference': 'concepts', 'version': concepts.__version__,
                  'requests': requests, 'closure_checks': closures,
                  'empty_axis_requests_not_crosschecked': skipped_empty,
                  'scope': 'domain/final-observed/event-observed closures and supports, not exploration scheduling'}))
