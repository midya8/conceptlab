import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from conceptlab.core import audit
from conceptlab.exploration import explore, validate_exploration
from conceptlab.exploration_verify import verify_exploration

ROOT = Path(__file__).resolve().parents[1]


class ExplorationTests(unittest.TestCase):
    def test_all_small_expert_families_and_every_initial_subfamily(self):
        count = 0
        for m in range(4):
            for family in range(1 << (1 << m)):
                rows = [[a for a in range(m) if r >> a & 1] for r in range(1 << m) if family >> r & 1]
                canonical = {(r['premise_mask'], r['conclusion_mask']) for r in audit({'attributes': m, 'objects': rows})['canonical_basis']}
                for initial in range(1 << len(rows)):
                    data = {'context': {'attributes': m, 'objects': rows}, 'initial_objects': [i for i in range(len(rows)) if initial >> i & 1]}
                    report = explore(data)
                    self.assertTrue(verify_exploration(report))
                    self.assertEqual(canonical, {(r['premise_mask'], r['conclusion_mask']) for r in report['basis']})
                    count += 1
        self.assertEqual(count, 6654)

    def test_seeded_duplicates_order_and_bounds(self):
        rng = random.Random(6481)
        for _ in range(300):
            m = rng.randrange(6)
            rows = [[a for a in range(m) if rng.randrange(2)] for _ in range(rng.randrange(9))]
            ids = [i for i in range(len(rows)) if rng.randrange(2)]
            rng.shuffle(ids)
            data = {'context': {'attributes': m, 'objects': rows}, 'initial_objects': ids}
            before = copy.deepcopy(data)
            r = explore(data)
            self.assertEqual(data, before)
            self.assertTrue(verify_exploration(r))
            self.assertLessEqual(len(r['events']), (1 << m) + len(rows))
            self.assertEqual(r['question_count'], r['accept_count'] + r['reject_count'])

    def test_all_controls_and_counterexample_protocol(self):
        for control in json.loads((ROOT / 'docs/exploration-controls.json').read_text()):
            r = explore(control['input'])
            self.assertTrue(verify_exploration(r))
            for i, e in enumerate(r['events']):
                if e['response'] == 'reject':
                    self.assertEqual(e['selected_counterexample'], min(e['counterexample_ids']))
                    self.assertEqual(r['events'][i + 1]['premise_mask'], e['premise_mask'])
                    self.assertNotEqual(r['events'][i + 1]['observed_closure_mask'], e['observed_closure_mask'])
        hidden = explore(json.loads((ROOT / 'examples/exploration.json').read_text()))
        self.assertEqual(hidden['events'][0]['response'], 'reject')
        self.assertEqual(hidden['events'][0]['known_before'], [0])

    def test_schema(self):
        good = {'context': {'attributes': 2, 'objects': [[0], [1]]}, 'initial_objects': []}
        for bad in [None, [], {}, {**good, 'extra': 1}, {**good, 'context': {'attributes': 6, 'objects': []}}, {**good, 'context': {'attributes': True, 'objects': []}}, {**good, 'context': {'attributes': 2, 'objects': [[True]]}}, {**good, 'context': {'attributes': 2, 'objects': [[0, 0]]}}, {**good, 'initial_objects': [True]}, {**good, 'initial_objects': [2]}, {**good, 'initial_objects': [-1]}, {**good, 'initial_objects': [0, 0]}, {**good, 'initial_objects': None}]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                explore(bad)

    def test_every_scalar_forgery_rejected(self):
        reports = [explore(c['input']) for c in json.loads((ROOT / 'docs/exploration-controls.json').read_text())]
        count = 0
        def leaves(x, path=()):
            if isinstance(x, dict):
                for k, v in x.items():
                    if not path and k == 'input':
                        continue
                    yield from leaves(v, path + (k,))
            elif isinstance(x, list):
                for k, v in enumerate(x):
                    yield from leaves(v, path + (k,))
            else:
                yield path, x
        for report in reports:
            for path, value in leaves(report):
                forged = copy.deepcopy(report)
                target = forged
                for k in path[:-1]:
                    target = target[k]
                target[path[-1]] = not value if type(value) is bool else value + 1 if type(value) is int else 'forged'
                with self.assertRaises(ValueError, msg=str(path)):
                    verify_exploration(forged)
                count += 1
            for key in report:
                forged = copy.deepcopy(report)
                del forged[key]
                with self.assertRaises(ValueError):
                    verify_exploration(forged)
            with self.assertRaises(ValueError):
                verify_exploration({**report, 'extra': 1})
        self.assertGreater(count, 3000)

    def test_verifier_does_not_call_generator(self):
        r = explore(json.loads((ROOT / 'examples/exploration.json').read_text()))
        with patch('conceptlab.exploration.explore', side_effect=AssertionError('generator called')):
            self.assertTrue(verify_exploration(r))

    def test_cli_roundtrip_and_atomic_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory) / 'report.json'
            run = lambda args, **kw: subprocess.run([sys.executable, '-m', 'conceptlab', *args], capture_output=True, **kw)
            r = run(['--exploration', str(ROOT / 'examples/exploration.json'), '-o', str(dest)])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(run(['--verify-exploration', str(dest)]).returncode, 0)
            report = json.loads(dest.read_text())
            report['complete'] = False
            forged = json.dumps(report).encode()
            for args, body in [(['--verify-exploration', '-'], forged), (['--exploration', '-'], b'{"context":{},"context":{}}'), (['--exploration', '-'], b'NaN'), (['--exploration', '-'], b'\xff'), (['--exploration', '-'], b' ' * 65537), (['--partial', '--exploration', '-'], b'{}')]:
                old = dest.read_bytes()
                bad = run(args + ['-o', str(dest)], input=body)
                self.assertEqual(bad.returncode, 2, bad.stderr)
                self.assertEqual(dest.read_bytes(), old)
            dest.write_text('{}')
            self.assertEqual(run(['--verify-exploration', str(dest)]).returncode, 2)


if __name__ == '__main__':
    unittest.main()
