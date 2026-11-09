"""Original completion controls. Expected reports are generated, not hand-written."""
from pathlib import Path
import json
from conceptlab.partial import audit_partial

def goal(p,q):return {'premise':p,'conclusion':q}
cases=[
 ('Unknown is not false',{'attributes':2,'objects':[[None,0]],'goals':[goal([], [0]),goal([0],[1])]}),
 ('Both extreme fill-ins pass, an intermediate completion fails',{'attributes':2,'objects':[[None,None]],'goals':[goal([0],[1])]}),
 ('Overlapping premise remains a tautology',{'attributes':1,'objects':[[None]],'goals':[goal([0],[0])]}),
 ('No objects: certain validity without observed support',{'attributes':2,'objects':[],'goals':[goal([], [0]),goal([1],[0])]}),
 ('No attributes',{'attributes':0,'objects':[[],[]],'goals':[goal([],[])]}),
 ('Both universes empty',{'attributes':0,'objects':[],'goals':[]}),
 ('Known counterexample cannot be completed away',{'attributes':2,'objects':[[1,0],[None,1]],'goals':[goal([0],[1])]}),
 ('Known implication and uncertain support',{'attributes':2,'objects':[[None,1],[0,0]],'goals':[goal([0],[1])]}),
 ('Duplicate objects retain distinct witness identities',{'attributes':2,'objects':[[None,0],[None,0]],'goals':[goal([], [0]),goal([0],[1])]}),
 ('Six unknowns: every one of 64 completions',{'attributes':3,'objects':[[None,None,None],[None,None,None]],'goals':[goal([0],[1]),goal([1],[2]),goal([], [0]),goal([2],[0])]}),
 ('All known: singleton completion',{'attributes':4,'objects':[[1,1,0,0],[0,1,1,0],[1,0,0,1],[0,0,1,1]],'goals':[goal([0],[1]),goal([0],[0]),goal([], [2])]}),
 ('Repeated goals preserve positions',{'attributes':2,'objects':[[None,0]],'goals':[goal([], [0]),goal([], [0]),goal([0],[1]),goal([],[])]}),
]
root=Path(__file__).resolve().parents[1]
inputs=[{'name':name,'input':data} for name,data in cases]
(root/'docs/partial-controls.json').write_text(json.dumps(inputs,indent=2)+'\n')
(root/'examples/partial.json').write_text(json.dumps(inputs[0]['input'],indent=2)+'\n')
reports=[audit_partial(data) for _,data in cases]
assert reports[0]['goal_subsets'][3]['possible'] is False
assert reports[1]['queries'][6]['valid_completions']==[0,2,3]
assert reports[2]['queries'][3]['certain']
print(json.dumps({'controls':len(reports),'completions':sum(len(r['completions']) for r in reports),'queries':sum(len(r['queries']) for r in reports),'query_completion_pairs':sum(len(r['queries'])*len(r['completions']) for r in reports),'goal_subsets':sum(len(r['goal_subsets']) for r in reports),'minimal_conflicts':sum(len(r['minimal_impossible_goal_sets']) for r in reports)}))
