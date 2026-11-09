"""Original synthetic contexts; no copied datasets or examples."""
import json
from pathlib import Path
from conceptlab import audit

controls=[
 ('No objects: every implication is vacuous',3,[]),
 ('No attributes: one concept, all objects',0,[[],[],[]]),
 ('Completely empty context',0,[]),
 ('Shared attribute follows from empty premise',3,[[0],[0,1],[0,2],[0,1,2]]),
 ('Duplicate rows change support, not concepts',3,[[0],[0],[1,2]]),
 ('Contradictory antecedent has zero support',3,[[0,2],[1,2]]),
 ('All rows have every attribute',4,[list(range(4))]*3),
 ('Contranominal context retains every closed subset',4,[[a for a in range(4) if a!=g] for g in range(4)]),
 ('Implication direction is not reversible',3,[[0,1],[1],[1,2],[]]),
 ('One new object invalidates a former implication',3,[[0,1],[1],[0],[1,2],[]]),
 ('Six attributes, eight original signatures',6,[[0,1],[0,2],[1,3],[2,4],[3,5],[0,4,5],[1,2,5],[]]),
]
# Search deterministic tiny contexts for strict explanatory controls, not performance selection.
found={}
for bits in range(1<<12):
 rows=[[a for a in range(4) if bits>>(g*4+a)&1] for g in range(3)]
 r=audit({'attributes':4,'objects':rows});subsets=r['attribute_subsets']
 nonclosed={x['mask'] for x in subsets if not x['closed']}
 pseudo={x['premise_mask'] for x in r['canonical_basis']}
 if 'pseudo' not in found and any(any(q!=p and q&p==q for q in nonclosed) for p in pseudo):found['pseudo']=rows
 if 'join' not in found and any(
   (r['concepts'][op['left']]['extent_mask']|r['concepts'][op['right']]['extent_mask'])!=r['concepts'][op['join']]['extent_mask'] for op in r['lattice_operations']):found['join']=rows
 if 'chain' not in found and any(len(t['steps'])>=2 for t in r['closure_traces']):found['chain']=rows
 if len(found)==3:break
assert len(found)==3
controls.extend([('Pseudo-intent need not be minimal nonclosed',4,found['pseudo']),('Join is not raw union of extents',4,found['join']),('Closure needs more than one rule application',4,found['chain'])])
reports=[]
for name,m,rows in controls:
 data={'attributes':m,'objects':rows};reports.append({'name':name,'input':data,'report':audit(data)})
root=Path(__file__).resolve().parents[1]
(root/'docs/audits.json').write_text(json.dumps(reports,separators=(',',':'))+'\n')
(root/'examples/demo.json').write_text(json.dumps(reports[11]['input'],indent=2)+'\n')
print(json.dumps({'controls':len(reports),'attribute_subsets':sum(len(r['report']['attribute_subsets']) for r in reports),'object_subsets':sum(len(r['report']['object_subsets']) for r in reports),'concepts':sum(len(r['report']['concepts']) for r in reports),'rules':sum(len(r['report']['canonical_basis']) for r in reports),'bytes':(root/'docs/audits.json').stat().st_size,'strict_controls':found}))
