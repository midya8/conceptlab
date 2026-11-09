import unittest
from itertools import combinations
from conceptlab import audit, validate


def reference(data):
    m, rows = data['attributes'], list(map(set, data['objects']))
    universe = set(range(m))
    sets = [set(a for a in range(m) if b >> a & 1) for b in range(1 << m)]
    def closed(b):
        supporting = [row for row in rows if b <= row]
        return set.intersection(universe, *supporting)
    closure = list(map(closed, sets))
    pseudo = []
    for b in sorted(sets, key=lambda s: (len(s), sorted(s))):
        if b != closed(b) and all(closed(q) <= b for q in pseudo if q < b):
            pseudo.append(b)
    def mask(s):
        return sum(1 << a for a in s)
    return [mask(s) for s in closure], {mask(s) for s in pseudo}


class Tests(unittest.TestCase):
    def check_context(self, data):
        report = audit(data)
        closures, pseudo = reference(data)
        self.assertEqual([s['closure_mask'] for s in report['attribute_subsets']], closures)
        self.assertEqual({p['premise_mask'] for p in report['canonical_basis']}, pseudo)
        m=data['attributes']
        closed_masks=[b for b,c in enumerate(closures) if b==c]
        self.assertEqual(report['next_closure']['intents'],sorted(closed_masks,key=lambda b:tuple((b>>a)&1 for a in range(m))))
        for a,c in enumerate(closures):
            self.assertEqual(a&c,a);self.assertEqual(closures[c],c)
            for b,d in enumerate(closures):
                if a&b==a:self.assertEqual(c&d,c)
        concepts = report['concepts']
        below = lambda x,y: x['extent_mask'] & y['extent_mask'] == x['extent_mask']
        for op in report['lattice_operations']:
            x,y=concepts[op['left']], concepts[op['right']]
            lowers=[z for z in concepts if below(z,x) and below(z,y)]
            uppers=[z for z in concepts if below(x,z) and below(y,z)]
            meet,join=concepts[op['meet']], concepts[op['join']]
            self.assertTrue(all(below(z,meet) for z in lowers))
            self.assertTrue(all(below(join,z) for z in uppers))
            self.assertIn(meet,lowers);self.assertIn(join,uppers)
        # Model enumeration checks complete basis semantics, not its forward implementation.
        basis=report['canonical_basis']
        models=[b for b in range(1<<data['attributes']) if all(
            b&r['premise_mask']!=r['premise_mask'] or b&r['conclusion_mask']==r['conclusion_mask'] for r in basis)]
        self.assertEqual(models,[s['mask'] for s in report['attribute_subsets'] if s['closed']])
        # Independent rule-removal models check every recorded irredundancy certificate.
        for proof in report['basis_irredundancy']:
            removed=basis[proof['removed_rule']];w=proof['model_mask']
            self.assertEqual(w&removed['premise_mask'],removed['premise_mask'])
            self.assertNotEqual(w&removed['conclusion_mask'],removed['conclusion_mask'])
            for rule in basis:
                if rule!=removed:
                    self.assertTrue(w&rule['premise_mask']!=rule['premise_mask'] or w&rule['conclusion_mask']==rule['conclusion_mask'])
        # Explicit Galois connection over all object/attribute subset pairs.
        for obj in report['object_subsets']:
            for attrs in report['attribute_subsets']:
                self.assertEqual(obj['mask']&attrs['extent_mask']==obj['mask'],
                                 attrs['mask']&obj['intent_mask']==attrs['mask'])
        return report

    def test_all_689_contexts_through_three_by_three(self):
        for m in range(4):
            for n in range(4):
                for bits in range(1<<(m*n)):
                    self.check_context({'attributes':m,'objects':[[a for a in range(m) if bits>>(g*m+a)&1] for g in range(n)]})

    def test_empty_context_vacuity(self):
        r=self.check_context({'attributes':3,'objects':[]})
        self.assertEqual(len(r['concepts']),1)
        self.assertEqual(r['canonical_basis'][0]['premise_mask'],0)
        self.assertEqual(r['canonical_basis'][0]['conclusion_mask'],7)
        self.assertTrue(all(s['support_denominator']==0 for s in r['attribute_subsets']))

    def test_no_attributes(self):
        r=self.check_context({'attributes':0,'objects':[[],[]]})
        self.assertEqual(r['concepts'],[{'id':0,'intent_mask':0,'extent_mask':3}])

    def test_duplicate_rows_preserve_counts(self):
        r=self.check_context({'attributes':2,'objects':[[0],[0],[1]]})
        self.assertEqual(r['attribute_subsets'][1]['support_count'],2)

    def test_all_masks_closed_contranominal(self):
        r=self.check_context({'attributes':4,'objects':[[a for a in range(4) if a!=g] for g in range(4)]})
        self.assertEqual(len(r['concepts']),16);self.assertEqual(r['canonical_basis'],[])

    def test_full_rows(self):
        r=self.check_context({'attributes':6,'objects':[list(range(6))]*8})
        self.assertEqual(len(r['concepts']),1)

    def test_invalid_types_and_bounds(self):
        for data in [None,{}, {'attributes':True,'objects':[]},{'attributes':7,'objects':[]},
                     {'attributes':1,'objects':[[True]]},{'attributes':1,'objects':[[0,0]]},
                     {'attributes':1,'objects':[[1]]},{'attributes':1,'objects':[[]]*9}]:
            with self.assertRaises(ValueError):audit(data)

    def test_input_unchanged_and_order_canonical(self):
        d={'attributes':3,'objects':[[2,0],[1]]}
        r=audit(d);self.assertEqual(d['objects'][0],[2,0]);self.assertEqual(r['context']['objects'][0],[0,2])

    def test_seeded_larger_independent(self):
        import random
        rng=random.Random(20691109)
        for _ in range(100):
            m=rng.randint(4,6);n=rng.randrange(9)
            self.check_context({'attributes':m,'objects':[[a for a in range(m) if rng.randrange(2)] for _ in range(n)]})

if __name__=='__main__':unittest.main()
