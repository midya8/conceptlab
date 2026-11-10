/* Finite exact-expert exploration. Independent browser bitset implementation. */
export function explore(data){
 const record=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
 const exact=(x,keys)=>record(x)&&Object.keys(x).sort().join('|')===keys.slice().sort().join('|');
 if(!exact(data,['context','initial_objects'])||!exact(data.context,['attributes','objects']))throw Error('Expected context and initial_objects');
 const {attributes:m,objects}=data.context;
 if(!Number.isInteger(m)||m<0||m>5||!Array.isArray(objects)||objects.length>8)throw Error('Use 0..5 attributes and at most eight objects');
 const rows=objects.map(row=>{if(!Array.isArray(row)||row.some(a=>!Number.isInteger(a)||a<0||a>=m)||new Set(row).size!==row.length)throw Error('Objects need unique valid attribute indices');return row.reduce((v,a)=>v|(1<<a),0);});
 if(!Array.isArray(data.initial_objects)||data.initial_objects.some(i=>!Number.isInteger(i)||i<0||i>=rows.length)||new Set(data.initial_objects).size!==data.initial_objects.length)throw Error('initial_objects needs unique expert row indices');
 let known=data.initial_objects.slice().sort((a,b)=>a-b),basis=[],events=[],current=0;
 const full=(1<<m)-1,copy=x=>JSON.parse(JSON.stringify(x)),all=rows.map((_,i)=>i);
 function table(p,ids){const support=ids.filter(i=>(rows[i]&p)===p);return [support.reduce((c,i)=>c&rows[i],full),support];}
 function closure(seed){let result=seed;const rounds=[];while(true){const before=result,firing=[];basis.forEach((r,i)=>{if((r.premise_mask&before)===r.premise_mask){firing.push(i);result|=r.conclusion_mask;}});rounds.push({before,firing,added:result&~before,after:result});if(result===before)return [result,rounds];}}
 while(true){
  const [observed,support]=table(current,known),[domain,domain_support]=table(current,all),before_known=known.slice(),before_basis=copy(basis),question=observed!==current;
  const counters=question?all.filter(i=>(rows[i]&current)===current&&(rows[i]&observed)!==observed):[],response=question?(counters.length?'reject':'accept'):'closed',selected=counters.length?counters[0]:null;
  let accepted_id=null,successor=null;const attempts=[];
  if(response==='reject'){if(known.includes(selected))throw Error('Repeated counterexample');known=[...known,selected].sort((a,b)=>a-b);if(basis.some(r=>(rows[selected]&r.premise_mask)===r.premise_mask&&(rows[selected]&r.conclusion_mask)!==r.conclusion_mask))throw Error('Counterexample contradicts accepted knowledge');}
  else{
   if(response==='accept'){accepted_id=basis.length;basis.push({id:accepted_id,premise_mask:current,conclusion_mask:observed&~current,closure_mask:observed});}
   for(let pivot=m-1;pivot>=0;pivot--){if(current&(1<<pivot))continue;const lower=(1<<pivot)-1,seed=(current&lower)|(1<<pivot),[candidate,derivation]=closure(seed),diff=[];for(let a=0;a<pivot;a++)if(Boolean(candidate&(1<<a))!==Boolean(current&(1<<a)))diff.push(a);const allowed=diff.length===0;attempts.push({pivot,seed_mask:seed,closure_mask:candidate,derivation,earlier_disagreements:diff,accepted:allowed});if(allowed){successor=candidate;break;}}
  }
  events.push({id:events.length,premise_mask:current,known_before:before_known,basis_before:before_basis,observed_closure_mask:observed,observed_support:support,domain_closure_mask:domain,domain_support,question,conclusion_mask:observed&~current,response,counterexample_ids:counters,selected_counterexample:selected,selected_attributes_mask:selected===null?null:rows[selected],accepted_rule_id:accepted_id,known_after:known.slice(),basis_after:copy(basis),next_attempts:attempts,next_premise_mask:response==='reject'?current:successor});
  if(events.length>(1<<m)+rows.length)throw Error('Progress bound exceeded');
  if(response==='reject')continue;if(successor===null)break;current=successor;
 }
 const audit=[];
 for(let p=0;p<=full;p++){const [k,derivation]=closure(p),[d,ds]=table(p,all),[o,os]=table(p,known);if(k!==d||d!==o)throw Error('Incomplete final closure theory');const missing=[];for(let a=0;a<m;a++)if(!(d&(1<<a)))missing.push({attribute:a,object_ids:ds.filter(i=>!(rows[i]&(1<<a)))});audit.push({premise_mask:p,knowledge_closure_mask:k,domain_closure_mask:d,observed_closure_mask:o,domain_support:ds,observed_support:os,derivation,missing_attribute_counterexamples:missing});}
 return {schema:'conceptlab-exploration-v1',input:copy(data),events,basis,final_objects:known,unseen_objects:all.filter(i=>!known.includes(i)),closure_audit:audit,complete:true,question_count:events.filter(e=>e.question).length,accept_count:events.filter(e=>e.response==='accept').length,reject_count:events.filter(e=>e.response==='reject').length};
}
