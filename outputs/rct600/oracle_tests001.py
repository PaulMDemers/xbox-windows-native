"""Independent constructed positive and adversarial return trace controls."""
import json
from pathlib import Path
from trace_oracle import validate
K=Path(__file__).resolve().parent;out=K/'oracle-tests001.json';assert not out.exists()
lines=['IMAGE 00400000 00000001 00000000'];sites={};stacks={1:[],2:[]};ident=0
def site(address,api):
 if address not in sites:
  lines.append('BP %08x %08x %08x'%(len(sites),address,api));sites[address]=api
def call(tid,api,a,b,name=None):
 global ident
 ident+=1;sp=0x100000*tid-0x100*len(stacks[tid]);ret=0x401000 if api<3 else 0x402000
 target={1:0x77001000,2:0x77002000,3:0x50001000}[api];site(ret,0)
 if api<3:
  kind='LOAD' if api==1 else ('ORD' if isinstance(name,int) else 'PROC')
  lines.append('%s %08x %08x %08x %s'%(kind,tid,ret,0 if api==1 else a,'%08x'%name if isinstance(name,int) else name.encode().hex()))
 lines.append('CALL '+' '.join('%08x'%n for n in [ident,tid,api,ret,sp,a,b,target]))
 stacks[tid].append((ident,api,ret,sp))
def ret(tid,value):
 i,api,addr,sp=stacks[tid].pop();sp+=4+{1:4,2:8,3:0}[api]
 lines.append('RETURN '+' '.join('%08x'%n for n in [i,tid,api,addr,sp,value]))
def pair(tid,api,a,b,name,value):call(tid,api,a,b,name);ret(tid,value)
for i in range(2):
 site(0x77001000+i*0x1000,i+1);lines.append('ARM %08x %08x %08x'%(i,0x403000+i*4,0x77001000+i*0x1000))
pair(1,1,0x1234,0,'user32.dll',0x70000000)
pair(1,2,0x70000000,0x1234,'MessageBeep',0x70001000)
pair(1,1,0x1234,0,'xwn600-does-not-exist.dll',0)
call(1,1,0x1234,0,'C:\\xwn600-kit\\fixture.dll')
call(2,1,0x1234,0,'C:\\xwn600-kit\\fixture.dll');ret(2,0x50000000);ret(1,0x50000000)
def probe(tid,d,s):
 call(tid,3,d,s)
 if d:probe(tid,d-1,s+1)
 ret(tid,((s+d)^0x600abcde)+d*(d+1)//2)
for tid in [1,2]:
 for depth in range(4):
  pair(tid,2,0x50000000,0x1234,'probe600',0x50001000);site(0x50001000,3)
  pair(tid,2,0x50000000,7,7,0x50001000);probe(tid,depth,depth)
 pair(tid,2,0x50000000,0x1234,'missing600',0);pair(tid,2,0x50000000,8,8,0)
lines+=['TOTAL %08x %08x %08x'%(ident,ident,len(sites)),'END 00000000 0000002d 00000000']
good='\n'.join(lines)+'\n';positive=validate(good,0x400000,0x10000)
ri=next(i for i,l in enumerate(lines) if l.startswith('RETURN '))
def changed(i,field,value):
 a=lines.copy();p=a[i].split();p[field]=value;a[i]=' '.join(p);return '\n'.join(a)+'\n'
variants={
 'missing_return':'\n'.join(lines[:ri]+lines[ri+1:])+'\n',
 'duplicate_return':'\n'.join(lines[:ri]+[lines[ri]]+lines[ri:])+'\n',
 'wrong_thread':changed(ri,2,'00000002'),
 'wrong_frame':changed(ri,1,'00000002'),
 'wrong_address':changed(ri,4,'00401001'),
 'wrong_stack':changed(ri,5,'00100000'),
 'missing_success_result':changed(ri,6,'00000000'),
 'unresolved_end':good.replace('0000002d 00000000\n','0000002d 00000001\n'),
 'unknown_exception':good.replace('TOTAL ','EXCEPTION c0000005 1 1\nTOTAL '),
 'duplicate_end':good+lines[-1]+'\n',
 'false_probe_result':good.replace('600abcde','600abcdf'),
 'wrong_module':good.replace('50000000','00000000'),
 'missing_call':good.replace(next(x+'\n' for x in lines if x.startswith('CALL ')),''),
}
rejected=[]
for name,data in variants.items():
 try:validate(data,0x400000,0x10000)
 except (AssertionError,ValueError,KeyError,UnicodeError):rejected.append(name)
 else:raise AssertionError(name)
out.write_text(json.dumps(dict(passed=True,positive=positive,rejected=rejected,scope='Constructed parser controls, not an observed Windows run.'),indent=2)+'\n')
print('600 oracle: positive and13 rejection controls passed')
