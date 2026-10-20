"""Inspect exact failed trace without manufacturing a successful END or phase."""
import hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'failure-review001.json';assert not out.exists()
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
from dib_oracle import decode_header
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=Path('C:/xwn609/pc001/cold1-002/files/xwn609/trace.txt');lines=p.read_text().splitlines()
calls={};args={};headers={};returns={};outputs={};stacks=defaultdict(list);totals=[];ends=[];phase=[];termination=[];modules={};breakpoints={};unloads=[];absent=[]
nargs={1:1,2:2,3:9,4:6,5:3,6:1,7:3,8:4,9:1,10:2,11:13,12:0,13:6,14:2,15:1,16:1}
for n,line in enumerate(lines):
 s=line.split();kind=s[0]
 if kind in ['LOAD','PROC','ORD']:continue
 v=[int(x,16) for x in s[1:]]
 if kind=='CALL':
  i,tid,api,ret,sp,a,b,target=v;assert i==len(calls)+1
  calls[i]=dict(tid=tid,api=api,ret=ret,sp=sp);stacks[tid].append(i)
 elif kind=='ARGS':
  i,count,*a=v;assert i in calls and i not in args and count==len(a)==nargs[calls[i]['api']];args[i]=a
 elif kind=='RETURN':
  i,tid,api,ret,sp,value=v;c=calls[i];assert i not in returns and stacks[tid].pop()==i
  assert (tid,api,ret)==(c['tid'],c['api'],c['ret']) and sp==c['sp']+4+(0 if api in [14,15,16] else 4*nargs[api]);returns[i]=value
 elif kind=='DIB':
  i,address,status,count,stride,extent,*raw=v;api=calls[i]['api']
  assert address==args[i][1 if api==4 else 10 if api==11 else 0]
  assert i not in headers and count==len(raw) and (status,stride,extent)==decode_header(address,raw,status)
  headers[i]=dict(address=address,status=status,stride=stride,extent=extent,raw=raw)
 elif kind=='OUTPUT':
  i,api,address,value=v;assert address==args[i][{4:3,5:1,8:2}[api]] and address;outputs[i]=value
 elif kind=='OUTPUT_ABSENT':
  i,api,address=v;assert api==calls[i]['api']==4 and address==args[i][3]==0 and i in returns and i not in outputs
  outputs[i]=None;absent.append(i)
 elif kind=='MODULE':modules[v[0]]=v[1]
 elif kind=='BP':
  index,address,api,owner=v;assert index==len(breakpoints);breakpoints[index]=dict(address=address,api=api,owner=owner)
 elif kind=='UNLOAD_TRACKED':
  base,index,address=v;assert index in breakpoints and breakpoints[index]['address']==address and base in modules
  owned={j:b for j,b in breakpoints.items() if base<=b['address']<base+modules[base]}
  pending=[i for i,c in calls.items() if i not in returns and base<=c['ret']<base+modules[base]]
  unloads.append(dict(line=n,base=base,size=modules[base],first_index=index,first_address=address,owned=owned,pending_calls=pending))
 elif kind=='PHASE':phase.append(v)
 elif kind=='TERMINATE':termination.append(dict(line=n,values=v))
 elif kind=='TOTAL':totals.append(v)
 elif kind=='END':ends.append(v)
assert len(calls)==len(returns)==536 and not any(stacks.values())
assert totals==[[536,536,163]] and ends==[[97,536,1]] and not phase
assert len(termination)==1 and len(unloads)==2
first=unloads[0];assert (first['base'],first['first_index'],first['first_address'])==(0x71500000,129,0x7157e4de)
assert lines[termination[0]['line']-1].startswith('UNLOAD_TRACKED 71500000 ')
assert unloads[1]['line']>termination[0]['line']
assert not first['pending_calls'] and all(b['api']==0 for b in first['owned'].values())
assert absent==[406,407,461] and all(returns[i]!=0 for i in absent)
assert lines[-3]=='PHASE_END 00000000 000007fe 00000000'
source=(K/'trace.c').read_text()
guard=source.split('static BOOL unload601(DWORD base) {',1)[1].split('static BOOL addbp',1)[0]
assert 'event("UNLOAD_TRACKED",base,j,bp[j].address);return FALSE;' in guard
assert not any(word in guard for word in ['.enabled','.armed','.refs'])
log=Path('C:/xwn609/pc001/cold1-002/files/xwn609/runner.txt').read_text()
for marker in ['load_dialog_count=1','load_edit_count=1','load_path_readback=1','load_click_posted=1','load_dialog_gone=1','reacquire_timeout=1','registry_restored=1','restart_requested=1']:
 assert marker in log,marker
assert 'park_phase_requested=1' not in log and 'park_reference_match=1' not in log
r=dict(review_passed=True,runtime_passed=False,trace_sha256=sha(p),paired_calls=536,headers=len(headers),
 breakpoint_sites=len(breakpoints),absent_output_calls=absent,absent_bitmap_returns=[returns[i] for i in absent],
 unloads=unloads,phase_skipped_before_park=2046,no_park_phase=True,
 cause='Frozen unload601 rejects any recorded breakpoint address in an unloading module, irrespective of current armed/enabled/ref state. First marker directly precedes TERMINATE.',
 interpretation='All recorded calls returned; the first unloading module contains only recorded return sites and no pending return calls. This is trace reconstruction, not a live dump of armed/ref/step flags. Do not waive unload checks; qualify retirement and address reuse on a new original control first.',
 limits='Load dialog accepted exact save path and closed, but no reacquired game/loaded-scene proof. No save corruption, game crash, timing, FPS or acceleration conclusion. Second unload marker is after requested termination; stale GetLastError121 is not causal.')
out.write_text(json.dumps(r,indent=2)+'\n')
print('609 failed trace:536 pairs, absent outputs passed, first tracked DLL unload triggered termination')
