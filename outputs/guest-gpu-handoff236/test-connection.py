"""Execute actual pre-observation source with one-connection dashboard adapters."""
import copy,hashlib,json,time
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'connection-test001.json';assert not dest.exists()
source=k/'supervise-emulator.py';text=source.read_text();start=text.index('deadline=time.monotonic()+180');end=text.index('deadline=time.monotonic()+520',start)
body=compile(text[start:end],str(source),'exec');calls=[];checks=0
def connect(*args):calls.append(args);raise AssertionError('Observer consumed the sole prelaunch connection')
baseline=dict(closed=True,guest_resumed=True,remaining_breakpoints=[],physical_mode_restored=True,loader_launch=dict(status='accepted'),passed=True)
root=k/'artifacts/host-connection-test001';assert not root.exists();root.mkdir(parents=True)
for i,(change,accepted) in enumerate([({},True),({'passed':False},True),({'loader_launch':{'status':'requesting'}},False),({'guest_resumed':False},False)]):
 run=root/str(i);out=run/'out';out.mkdir(parents=True)
 (run/'startup-ready.json').write_text(json.dumps(dict(nic_ready=True)))
 (out/'trace-finished.signal').touch();trace=copy.deepcopy(baseline);trace.update(change);(out/'trace.json').write_text(json.dumps(trace))
 row=dict(cycles=[]);ns=dict(time=time,run=run,out=out,json=json,connect=connect,r=row,save=lambda:None,print=lambda *args,**kwargs:None)
 try:exec(body,ns);result=True
 except AssertionError:result=False
 assert result==accepted and not calls;checks+=2
 if accepted:assert row['diagnostic_passed']==trace['passed'] and row['cycles']==[trace['loader_launch']];checks+=2
dest.write_text(json.dumps(dict(passed=True,checks=checks,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),test_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),actual_pre_observation_source_executed=True,prelaunch_connections=0,preserved_failed_diagnostic=True,guest_launch=False,physical_access=False),indent=2)+'\n')
print('236 connection ownership checks',checks)
