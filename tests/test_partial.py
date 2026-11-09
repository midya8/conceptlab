import copy
from fractions import Fraction
from itertools import product
import json
from pathlib import Path
import random
import unittest
from conceptlab.partial import audit_partial
from conceptlab.core import audit

ROOT=Path(__file__).resolve().parents[1]

class PartialTests(unittest.TestCase):
    def verify(self,data):
        original=copy.deepcopy(data);r=audit_partial(data);self.assertEqual(data,original)
        m,n=data['attributes'],len(data['objects']);u=[(g,a) for g in range(n) for a in range(m) if data['objects'][g][a] is None]
        # Independent complete-matrix truth table, then keep only compatible worlds.
        if m*n<=6:
            worlds=[]
            for bits in product((0,1),repeat=m*n):
                mat=[list(bits[g*m:(g+1)*m]) for g in range(n)]
                if all(data['objects'][g][a] in (None,mat[g][a]) for g in range(n) for a in range(m)):
                    cid=sum(mat[g][a]*2**i for i,(g,a) in enumerate(u));worlds.append((cid,mat))
            worlds.sort()
        else:
            worlds=[]
            for bits in product((0,1),repeat=len(u)):
                mat=copy.deepcopy(data['objects'])
                for bit,(g,a) in zip(bits,u):mat[g][a]=bit
                worlds.append((sum(bit*2**i for i,bit in enumerate(bits)),mat))
            worlds.sort()
        self.assertEqual(len(r['completions']),len(worlds))
        allsets=[set(a for a in range(m) if mask//2**a%2) for mask in range(2**m)]
        observations={}
        for cid,mat in worlds:
            rows=[set(a for a in range(m) if mat[g][a]) for g in range(n)]
            full=audit({'attributes':m,'objects':[sorted(row) for row in rows]})
            self.assertEqual([s['closure_mask'] for s in r['completions'][cid]['attribute_subsets']],[s['closure_mask'] for s in full['attribute_subsets']])
            for i,p in enumerate(allsets):
                support=[g for g in range(n) if p<=rows[g]]
                for j,q in enumerate(allsets):
                    bad=[g for g in support if not q<=rows[g]]
                    observations[(cid,i,j)]=(support,bad)
        for query in r['queries']:
            p,q=query['premise_mask'],query['conclusion_mask'];valid=[];invalid=[];undef=[];ratios=[];supports=[]
            for cid,_ in worlds:
                support,bad=observations[cid,p,q]
                self.assertEqual(query['counterexamples'][cid],{'completion':cid,'counterexample_objects':bad})
                (invalid if bad else valid).append(cid);supports.append(len(support))
                if support:ratios.append((cid,Fraction(len(support)-len(bad),len(support))))
                else:undef.append(cid)
            self.assertEqual(query['valid_completions'],valid);self.assertEqual(query['invalid_completions'],invalid)
            self.assertEqual(query['certain'],len(valid)==len(worlds));self.assertEqual(query['possible'],bool(valid))
            self.assertEqual(query['status'],'certain' if not invalid else 'contingent' if valid else 'impossible')
            self.assertEqual([query['support_count_min'],query['support_count_max']],[min(supports),max(supports)])
            self.assertEqual(query['confidence_undefined_completions'],undef)
            for key,fn in [('confidence_min',min),('confidence_max',max)]:
                if not ratios:self.assertIsNone(query[key]);continue
                extreme=fn(f for _,f in ratios);b=query[key]
                self.assertEqual(Fraction(b['numerator'],b['denominator']),extreme)
                self.assertEqual(b['completions'],[cid for cid,f in ratios if f==extreme])
        for s in r['goal_subsets']:
            valid=[cid for cid,_ in worlds if all(not observations[(cid,)+divmod(r['goal_query_ids'][g],2**m)][1] for g in s['goals'])]
            self.assertEqual(s['valid_completions'],valid);self.assertEqual(s['possible'],bool(valid));self.assertEqual(s['certain'],len(valid)==len(worlds))
        conflictmasks=[s['mask'] for s in r['goal_subsets'] if not s['possible'] and not any(not t['possible'] and t['mask']!=s['mask'] and t['mask']&s['mask']==t['mask'] for t in r['goal_subsets'])]
        self.assertEqual([s['mask'] for s in r['minimal_impossible_goal_sets']],conflictmasks)
        for s in r['minimal_impossible_goal_sets']:
            for w in s['deletion_witnesses']:
                self.assertEqual(w['completions'],r['goal_subsets'][s['mask']-2**w['removed_goal']]['valid_completions']);self.assertTrue(w['completions'])
        return r

    def test_exhaustive_ternary_contexts(self):
        for m in range(3):
            for n in range(3):
                for values in product((0,1,None),repeat=m*n):
                    self.verify({'attributes':m,'objects':[list(values[g*m:(g+1)*m]) for g in range(n)],'goals':[{'premise':[],'conclusion':list(range(m))},{'premise':list(range(m)),'conclusion':[]}]})

    def test_seeded_larger(self):
        rng=random.Random(831)
        for _ in range(60):
            m,n=rng.randrange(5),rng.randrange(5);rows=[[rng.randrange(2) for _ in range(m)] for _ in range(n)]
            cells=[(g,a) for g in range(n) for a in range(m)];rng.shuffle(cells)
            for g,a in cells[:rng.randrange(min(6,len(cells))+1)]:rows[g][a]=None
            goals=[{'premise':[a for a in range(m) if rng.randrange(2)],'conclusion':[a for a in range(m) if rng.randrange(2)]} for _ in range(4)]
            self.verify({'attributes':m,'objects':rows,'goals':goals})

    def test_retained_strict_controls(self):
        controls=json.loads((ROOT/'docs/partial-controls.json').read_text());rs=[self.verify(c['input']) for c in controls]
        self.assertTrue(all(rs[0]['goal_subsets'][1<<i]['possible'] for i in range(2)));self.assertFalse(rs[0]['goal_subsets'][3]['possible'])
        q=rs[1]['queries'][6];self.assertIn(0,q['valid_completions']);self.assertIn(3,q['valid_completions']);self.assertIn(1,q['invalid_completions'])
        self.assertTrue(rs[2]['queries'][3]['certain']);self.assertTrue(rs[3]['queries'][1]['certain']);self.assertIsNone(rs[3]['queries'][1]['confidence_min'])
        self.assertEqual([c['id'] for c in rs[9]['completions']],list(range(64)))

    def test_reject_invalid(self):
        base={'attributes':2,'objects':[[None,0]],'goals':[]}
        invalid=[None,{},dict(base,extra=1),dict(base,attributes=True),dict(base,attributes=5),dict(base,objects=[[False,0]]),dict(base,objects=[[None]]),dict(base,objects=[[2,0]]),dict(base,objects=[[None,None]]*4),dict(base,goals=[{'premise':[0,0],'conclusion':[]}]),dict(base,goals=[{'premise':[True],'conclusion':[]}]),dict(base,goals=[{'premise':[],'conclusion':[],'extra':1}])]
        for x in invalid:
            with self.assertRaises(ValueError):audit_partial(x)
