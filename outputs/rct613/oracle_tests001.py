"""Synthetic parser adversaries, not runtime clock qualification."""
import copy,hashlib,json
from pathlib import Path
from cost_oracle import validate
K=Path(__file__).resolve().parent;out=K/'oracle-tests001.json';assert not out.exists()
def record(tag,i,q,t,k,u,ws=12*1024**2,page=12*1024**2,index=0):
 return f'{tag} {i} {index} {q:016x} {t} {k:016x} {u:016x} {ws} {ws} {page}'
# Independent modulus pow: LCG period divides2^32; fixed workload checksum
# independently evaluated once by ordinary scalar arithmetic outside the oracle.
checksum=1
for _ in range(33554432):checksum=(checksum*1664525+1013904223)&0xffffffff
p=['FREQ 00000000000003e8'];children=[]
for i in range(6):
 base=10000+i*10000;cpu=200000 if i<2 else 15000000
 p += [record('START',i,base,base,10000,10000),record('END',i,base+2200,base+2200,20000,20000+cpu),
       record('OBSERVER_START',i,base+1,base+1,10000,10000),record('OBSERVER_END',i,base+2201,base+2201,20000,20000)]
 periodic=i in [1,3,4]
 if periodic:p.append(record('SAMPLE',i,base+100,base+100,10000,10000,index=0))
 p.append(f'CASE {i} {int(periodic)} {int(periodic)} 0 0')
 c=['FREQ 00000000000003e8',record('ALLOC_BEFORE',i,base-20,base-20,0,0,4*1024**2,4*1024**2),
    record('READY',i,base-10,base-10,10000,10000),record('WORK_START',i,base+10,base+10,10000,10000),
    record('WORK_END',i,base+2010,base+2010,10000,10000+cpu),f'RESULT {i} {33554432 if i>=2 else 0} {checksum if i>=2 else 1}','PASS']
 children.append('\n'.join(c)+'\n')
p+=['CONTROL_PASS','RESTART'];parent='\n'.join(p)+'\n'
assert validate(parent,children)['passed']
tests={}
tests['missing_end']=(parent.replace(p[2]+'\n','',1),children)
tests['unknown_case']=(parent.replace('START 0 0 ','START 6 0 ',1),children)
tests['bad_frequency']=(parent.replace('FREQ 00000000000003e8','FREQ 0000000000000000'),children)
tests['missing_pass']=(parent.replace('CONTROL_PASS\n',''),children)
tests['wrong_case_count']=(parent.replace('CASE 1 1 1 0 0','CASE 1 1 2 0 0'),children)
tests['reversed_sample']=(parent.replace('SAMPLE 1 0 0000000000004e84','SAMPLE 1 0 0000000000000000'),children)
for name,idx,old,new in [
 ('wrong_checksum',2,f'RESULT 2 33554432 {checksum}','RESULT 2 33554432 0'),
 ('missing_memory_growth',0,str(12*1024**2),str(4*1024**2)),
 ('child_clock_jump',0,'WORK_END 0 0 0000000000002eea','WORK_END 0 0 000000000003ffff'),
 ('child_frequency_mismatch',0,'FREQ 00000000000003e8','FREQ 00000000000003e9'),
 ('busy_zero_cpu',2,f'{15010000:016x}',f'{10000:016x}'),
 ('sleep_busy_cpu',0,f'{210000:016x}',f'{20010000:016x}')]:
 c=copy.copy(children);assert old in c[idx],name;c[idx]=c[idx].replace(old,new);tests[name]=(parent,c)
rejected=[]
for name,(p,c) in tests.items():
 assert p!=parent or c!=children,name
 try:validate(p,c)
 except (AssertionError,ValueError,KeyError):rejected.append(name)
 else:raise AssertionError('accepted '+name)
out.write_text(json.dumps(dict(passed=True,rejected=rejected,checksum=checksum,source_sha256=hashlib.sha256((K/'cost_oracle.py').read_bytes()).hexdigest(),scope='Synthetic host parser checks only; no runtime/performance inference.'),indent=2)+'\n')
print('Cost oracle negative tests passed:',len(rejected))
