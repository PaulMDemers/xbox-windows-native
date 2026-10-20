"""Bounded dashboard observation after one admitted launch; never launches."""
import importlib.util,json,time
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('controller596',K/'controller001.py')
c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
out=K/'observation001.json';assert not out.exists()
launch=c.read(K/'launch001.json');assert launch['requested']
r=dict(started_utc=c.m.utc(),completed=False,dashboard_return=False,checks=[],remote_writes=[],launches=0,limit_seconds=900)
c.m.write_json(out,r);deadline=time.monotonic()+900
# Give the accepted launch time to leave its dashboard before testing return.
time.sleep(30)
while time.monotonic()<deadline:
 row=dict(utc=c.m.utc(),reachable=False)
 try:
  with c.m.connect(timeout=5) as f:
   row['reachable']=True
   # Authentication/ownership checks only. Collection removes the hook first.
  r['dashboard_return']=True
 except Exception as e:row['error_type']=type(e).__name__
 r['checks'].append(row);c.m.write_json(out,r)
 if r['dashboard_return']:break
 time.sleep(min(20,max(0,deadline-time.monotonic())))
r.update(completed=True,ended_utc=c.m.utc(),console_state='dashboard reachable; run and shutdown unproved' if r['dashboard_return'] else 'offline after bounded observation; screen state unknown',normal_shutdown_proved=False)
c.m.write_json(out,r);print(json.dumps(r))
