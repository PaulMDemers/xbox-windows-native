"""Three fixed NEW runs in order; once-only state guards, no failed case replay."""
import datetime,hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'matrix001.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text());assert read(k/'prelaunch-review001.json')['passed']
r=dict(closed=False,physical_access=False,independent_runs=True,cases=[],controller_pid=__import__('os').getpid())
def save():
 p=dest.with_suffix('.tmp');p.write_text(json.dumps(r,indent=2)+'\n');p.replace(dest)
try:
 for case in ['preserve001']:
  assert not (k/case/'host-state.json').exists() and not (k/case/'runner-start.json').exists()
  row=dict(case=case,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());r['cases'].append(row);save()
  with (k/case/'matrix-console.txt').open('x') as log:
   child=subprocess.Popen([sys.executable,'-B',str(k/'run-emulator.py'),case],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   row['controller_pid']=child.pid;save();row['exit_code']=child.wait(timeout=1600);save()
  state=read(k/case/'host-state.json');assert state['closed'] and state['cleanup_record_exists'] and state.get('audit_exit_code')==0
  row['closed']=True;row['trace_passed']=read(k/case/'trace.json')['passed'];row['audit_sha256']=hashlib.sha256((k/case/'audit.json').read_bytes()).hexdigest();save()
  assert row['trace_passed'],'Trace failed; preserve closed case and stop matrix'
  assert row['exit_code']==0,'Controller failure retained; do not start later cases blindly'
 r['completed']=True
except BaseException as e:r.update(error=repr(e),completed=False);raise
finally:
 r['closed']=all(v.get('closed',False) for v in r['cases']);r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print('238 matrix closed')
