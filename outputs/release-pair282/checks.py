"""Independent three-boundary/report/retained-state checks before guest resume."""
import re
import decode,transport,graph_base,graph_extra,edges
def report(text,candidate,ending=False):
 pairs=re.findall(r'(?<![\w])(\w+)=(\d+)',text)
 n={k:int(v) for k,v in pairs};assert len(n)==len(pairs)
 assert n['version']==281 and n['state']==(5 if ending else 3)
 assert n['reason']==n['native_grant']==0 and n['candidate']==int(candidate)
 assert n['mask']==(15 if candidate else 0) and n['armed']==n['post']==1 and n['sealed']==int(ending)
 records=[]
 for i in range(2):
  assert n[f'record{i}_present']==int(i==0 or ending)
  if i and not ending:
   assert not any(k.startswith('record1_') and k!='record1_present' for k in n);continue
  r=[n[f'record{i}_{j}'] for j in range(16)];records.append(r)
  assert r[:4]==[280,1 if i==0 else 4,int(candidate),3 if i==0 else 5]
  assert r[4:10]==[0,1,15 if candidate else 0,1,i,2 if i==0 else 3]
  assert r[10]>0 and r[11:13]==([3,4] if i==0 else [5,6]) and 0<r[14]<=r[15]<=r[13]
 for s in range(1,4):
  if s==3 and not ending:assert n['s3_state']==0;continue
  assert n[f's{s}_state']==5
  assert all(n[f's{s}_{key}']==0 for key in ['reason','overflow','accounting','shader_unknown'])
  assert 0<n[f's{s}_rows']<=180000 and n[f's{s}_pages']==(n[f's{s}_rows']+255)//256
 return n,records

def pair(records,groups,candidate):
 assert len(groups)==2 and len(records)==1
 a,b=groups;r=records[0]
 results=[decode.validate(g,i+1,candidate) for i,g in enumerate(groups)]
 timing=[next(v for v in g if v[0]==71) for g in groups]
 assert timing[0][2]==timing[1][2]==r[10] and timing[0][4]<=timing[1][3]==r[14]
 assert timing[1][4]<=r[15]<=r[13]
 assert results[0]['mutation_clock']==results[1]['mutation_clock']
 assert sorted(v[:7] for v in a if v[0]==17)==sorted(v[:7] for v in b if v[0]==17)
 for kind in [66,67]:assert sorted(v for v in a if v[0]==kind)==sorted(v for v in b if v[0]==kind)
 selected={v[2] for v in a if v[0]==67};expected=[]
 for original in a:
  if original[0]==17 or original[0]>=64:continue
  row=original.copy()
  if candidate:
   if row[0]==3:assert row[2] in selected and row[3]==0;row[2]=0;row[4]=1
   elif row[0] in (4,5) and row[1] in selected:
    assert row[2]==2;row[2]=1
    if row[0]==5:assert row[3:5]==[1,1];row[4]=0
  expected.append(row)
 assert expected==[v for v in b if v[0]<64 and v[0]!=17]
 return dict(pre_post_clock=results[0]['mutation_clock'],retained_graph_exact=True)

def graph(g,ui,stage,allocations,candidate):
 assert all(r[0] in set(range(1,19))|set(range(30,34))|set(range(50,73)) for r in g)
 boundary=decode.validate_graph(g,stage,allocations,candidate)
 base=graph_base.inspect([r for r in g if r[0]<50],[r for r in ui if r[0]<50])
 extension=graph_extra.inspect(g,ui);assert extension['unknown_actor_work']==0
 return dict(boundary=boundary,base=base,extension=extension)

def initial(text,groups,ui,allocations,candidate):
 n,records=report(text,candidate);assert len(groups)==2
 analyses=[graph(g,ui,i+1,allocations,candidate) for i,g in enumerate(groups)]
 for s,g in enumerate(groups,1):assert len(g)==n[f's{s}_rows']
 edge=edges.inspect(groups[0],ui,allocations)
 assert analyses[0]['extension']['native_contexts']==analyses[1]['extension']['native_contexts']
 return dict(records=records,graphs=analyses,retained=pair(records,groups,candidate),unbound_edges=edge)

def final(firsttext,endtext,groups,ui,allocations,candidate):
 a,initialrecords=report(firsttext,candidate);b,records=report(endtext,candidate,True)
 assert records[0]==initialrecords[0] and all(a[k]==b[k] for k in a if k.startswith(('s1_','s2_','record0_')))
 assert len(groups)==3
 analyses=[graph(g,ui,i+1,allocations,candidate) for i,g in enumerate(groups)]
 assert all(len(g)==b[f's{s}_rows'] for s,g in enumerate(groups,1))
 assert all(v['extension']['native_contexts']==analyses[0]['extension']['native_contexts'] for v in analyses)
 return dict(transport=transport.inspect(records,groups,candidate),records=records,graphs=analyses)
