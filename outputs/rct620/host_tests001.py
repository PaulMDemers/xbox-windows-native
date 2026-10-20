"""Qualify balanced suspension and independent snapshot rejection rules."""
import copy,hashlib,json,os,subprocess
from pathlib import Path
from sample_oracle import validate_case
from serial_host import Lines
K=Path(__file__).resolve().parent;out=K/'host-tests001.json';assert not out.exists()
r=dict(passed=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
try:
 assert os.environ.get('XWN_BUILD_LEASE')=='held'
 O=Path('/mnt/c/xwn620/host001');O.mkdir(parents=True,exist_ok=False)
 cmd=['cc','-std=c99','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I',str(K),str(K/'host_suspend.c'),'-o',str(O/'suspend')]
 subprocess.run(cmd,check=True);subprocess.run([str(O/'suspend')],check=True,timeout=10)
 assert (K/'counter.h').read_bytes()==(K.parent/'rct617/counter.h').read_bytes()
 original=dict(identity=[200,204,100,12345],ticks=[10000,30000],host_seconds=20,cpu=19.8,thread_cpu=19.8,observer_cpu=.1,
  modules=[[0x400000,0x10000,'C:\\xwn620-kit\\subject.exe'],[0x77f00000,0x100000,'C:\\WINNT\\system32\\ntdll.dll']],
  ranges=[0x401000,0x401020,0x401030,0x401050],mode=1,loops=100,subject_pass=True,exit_code=0,observed=True,
  samples=[[i,10000+i*100,0x401005,0x120000,0,0x1b,0,0,1] for i in range(200)])
 validate_case(original);rejected=[]
 mutations=[('identity',lambda c:c['identity'].__setitem__(2,200)),('clock',lambda c:c.update(host_seconds=19)),
 ('cpu-negative',lambda c:c.update(cpu=-1)),('cpu-excess',lambda c:c.update(cpu=30)),
 ('thread-coverage',lambda c:c.update(thread_cpu=10)),('module-overlap',lambda c:c['modules'].append([0x400100,20,'bad'])),
 ('range-outside',lambda c:c['ranges'].__setitem__(0,0x300000)),('subject-fail',lambda c:c.update(subject_pass=False)),
 ('unowned-ip',lambda c:c['samples'][0].__setitem__(2,1)),('wrong-cpl',lambda c:c['samples'][0].__setitem__(5,8)),
 ('pre-suspended',lambda c:c['samples'][0].__setitem__(7,1)),('unbalanced-resume',lambda c:c['samples'][0].__setitem__(8,2)),
 ('long-hold',lambda c:c['samples'][0].__setitem__(6,101)),('sample-index',lambda c:c['samples'][0].__setitem__(0,1)),
 ('sample-order',lambda c:c['samples'][1].__setitem__(1,10000)),('sample-outside',lambda c:c['samples'][0].__setitem__(1,9999)),
 ('too-few',lambda c:c.update(samples=c['samples'][:20])),('idle-busy',lambda c:c.update(cpu=.1,thread_cpu=.1)),
 ('wrong-busy-location',lambda c:[v.__setitem__(2,0x77f01000) for v in c['samples']]),
 ('observer-excess',lambda c:c.update(observer_cpu=4)),('unexpected-samples',lambda c:c.update(observed=False))]
 for name,fn in mutations:
  c=copy.deepcopy(original);fn(c)
  try:validate_case(c)
  except AssertionError:rejected.append(name)
  else:raise AssertionError('Accepted invalid '+name)
 runner=(K/'runner.c').read_text();assert runner.index('sample619(&call')<runner.index('s->hold=GetTickCount()-start')
 assert 'SetThreadPriority(GetCurrentThread(),THREAD_PRIORITY_HIGHEST)' in runner
 assert 'GetThreadTimes(pi.hThread' in runner and 'modules(pi.hProcess,1)' in runner
 serial=Lines()
 for case in range(9):
  for kind in ['START','END']:
   line=('MARK %s %d %d\r\n'%(kind,case,case*20000+(0 if kind=='START' else 10000))).encode()
   for byte in line:serial.feed(bytes([byte]),len(serial.rows)+1)
 serial.finish();assert len(serial.rows)==18 and serial.rows[-1]['case']==8
 for name,line in [('case9',b'MARK START 9 0\n'),('negative',b'MARK START -1 0\n'),('kind',b'MARK BAD 1 0\n'),('overflow',b'MARK START 1 4294967296\n')]:
  try:Lines().feed(line,1)
  except AssertionError:rejected.append('serial-'+name)
  else:raise AssertionError(name)
 partial=Lines();partial.feed(b'MARK START 0',1)
 try:partial.finish()
 except AssertionError:rejected.append('serial-partial')
 else:raise AssertionError('partial accepted')
 r.update(passed=True,suspension_cases=7,rejections=rejected,commands=[cmd],sources={p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.S','.py']})
except BaseException as e:r['error']=repr(e);raise
finally:out.write_text(json.dumps(r,indent=2)+'\n')
print('Balanced suspension,21 snapshot negatives, all18 markers and5 serial negatives passed')
