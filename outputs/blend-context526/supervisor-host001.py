"""Actual subprocess supervisor with tiny owned stand-in child programs."""
import hashlib,importlib.util,json
from pathlib import Path
K=Path(__file__).resolve().parent;O=Path('C:/xwn526/supervisor-host001');assert not O.exists();O.mkdir(parents=True)
spec=importlib.util.spec_from_file_location('supervisor526',K/'supervise.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
cases=[]
for name,source in [('success','print("owned child complete")'),('failure','raise SystemExit(7)'),('timeout','import time; time.sleep(30)')]:
 m.K=O/name;m.K.mkdir();m.LOG=m.K/'logs';m.LIMITS={'launch':0.5}
 (m.K/'physical.py').write_text(source)
 r=m.run('launch');assert r['closed'] and not r['remote_retry_allowed']
 assert r['completed']==(name=='success') and r['deadline_reached']==(name=='timeout')
 if name=='failure':assert r['exit_code']==7
 try:m.run('launch')
 except AssertionError:pass
 else:raise AssertionError('action retried')
 cases.append(dict(case=name,result=r,duplicate_refused=True))
r=dict(passed=True,actual_subprocesses=True,real_network=False,all_children_closed=True,cases=cases,
       source_sha256=hashlib.sha256((K/'supervise.py').read_bytes()).hexdigest(),
       files={str(p):dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in O.rglob('*') if p.is_file()})
(K/'supervisor-host001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode());print('PASS three actual owned child lifetimes and repeat refusals')
