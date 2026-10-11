"""Bounded lease retries BEFORE any fresh case exists, never repeat a started prep."""
import datetime,json,subprocess,time
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'preparation-host001.json';assert not dest.exists() and not (k/'seed001').exists()
r=dict(physical_access=False,guest_launch=False,attempts=[],closed=False);deadline=time.monotonic()+600
try:
 for i in range(1,42):
  p=k/('preparation-resource%d-console.txt'%i)
  with p.open('x',encoding='utf-8') as log:code=subprocess.run(['pwsh','-NoProfile','-File',str(k/'Prepare.ps1'),'-Case','seed001'],stdout=log,stderr=subprocess.STDOUT).returncode
  busy="Xbox resource 'build' is busy or unavailable" in p.read_text()
  r['attempts'].append(dict(attempt=i,exit_code=code,resource_busy=busy,case_exists=(k/'seed001').exists()))
  if code==0:r['passed']=True;break
  assert busy and not (k/'seed001').exists() and time.monotonic()<deadline,'Preserve started preparation; no retry'
  time.sleep(15)
 else:raise AssertionError('Preparation lease attempt limit')
except BaseException as e:r.update(passed=False,error=repr(e));raise
finally:r.update(closed=True,closed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dest.write_text(json.dumps(r,indent=2)+'\n')
print('238 one preparation CLOSED')
