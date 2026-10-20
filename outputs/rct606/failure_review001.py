"""Inspect exact failed trace without manufacturing a successful END or phase."""
import hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'failure-review001.json';assert not out.exists()
sys.path.insert(0,str(K.parents[1]/'work/python-packages'));import pefile
from dib_oracle import decode_header
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=Path('C:/xwn606/pc001/cold1-002/files/xwn606/trace.txt');lines=p.read_text().splitlines()
calls={};args={};headers={};returns={};outputs={};stacks=defaultdict(list);totals=[];ends=[];phase=[];termination=[]
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
 elif kind=='PHASE':phase.append(v)
 elif kind=='TERMINATE':termination.append(dict(line=n,values=v))
 elif kind=='TOTAL':totals.append(v)
 elif kind=='END':ends.append(v)
assert len(calls)==len(returns)==406 and not any(stacks.values())
assert totals==[[406,406,90]] and ends==[[97,406,1]] and not phase and len(termination)==1
last=calls[406];assert last['api']==4 and args[406][3]==0 and returns[406]!=0 and 406 not in outputs
assert headers[406]['status']==8 and headers[406]['raw'][4]==3
assert lines[termination[0]['line']-1].startswith('RETURN 00000196 ')
assert all(n>termination[0]['line'] for n,l in enumerate(lines) if l.startswith('EXCEPTION '))
source=(K/'trace.c').read_text();assert 'if(!address||!readmem(address,&pointer,4))return FALSE;' in source
pe=pefile.PE('C:/xwn566/transfer002/game/RCT.EXE');base=pe.OPTIONAL_HEADER.ImageBase;size=pe.OPTIONAL_HEADER.SizeOfImage
main={i:c for i,c in calls.items() if base<=c['ret']<base+size};dib=[i for i,c in main.items() if c['api']==4];stretch=[i for i,c in main.items() if c['api']==11]
assert len(dib)==1 and len(stretch)==32 and returns[dib[0]] and outputs[dib[0]]
assert all(args[i][9]==outputs[dib[0]] and headers[i]['raw']==headers[dib[0]]['raw'] for i in stretch)
raw=headers[dib[0]]['raw'];signed=lambda x:x if x<2**31 else x-2**32
r=dict(review_passed=True,runtime_passed=False,trace_sha256=sha(p),paired_calls=406,headers=len(headers),no_park_phase=True,
 deterministic_guard=dict(call=406,caller=last['ret'],output_address=0,returned_bitmap=returns[406],header=headers[406],
 interpretation='The frozen outputs601 guard must return FALSE for this null address after logging RETURN. ownedbreak then fails and the debugger terminates its child. Later access violation is after TERMINATE, not evidence of the initiating game fault. Stale GetLastError121 does not identify the guard.'),
 early_rct=dict(create_call=dib[0],bits=outputs[dib[0]],stretch_calls=stretch,width=signed(raw[1]),height=signed(raw[2]),bpp=raw[3]>>16,compression=raw[4],stride=headers[dib[0]]['stride'],extent=headers[dib[0]]['extent'],colors_used=raw[8],return_scanlines=sorted(set(returns[i] for i in stretch))),
 limits='Valid paired/header observations from a failed bounded debugger run. Only early samples; not loaded-park evidence, clocks, costs, frames or hardware acceleration.',
 contract_source='https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createdibsection',
 contract_limit='Microsoft describes ppvBits as an output pointer, without explicitly documenting NULL acceptance. This NT5 internal invocation returned a nonzero bitmap with NULL. A new original NT5 control is required; do not infer universal API support.')
out.write_text(json.dumps(r,indent=2)+'\n');print('606 failed run preserved; deterministic NULL output guard and early RCT layout identified')
