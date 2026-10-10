"""Wait only for pre-source lease refusal; once build starts never repeat it."""
import datetime,hashlib,json,subprocess,time
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'host-build-state.json';assert not dest.exists()
assert not (k/'build001.json').exists()
r=dict(closed=False,physical_access=False,guest_launch=False,attempts=[],source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
def save():
 p=dest.with_suffix('.tmp');p.write_text(json.dumps(r,indent=2)+'\n');p.replace(dest)
try:
 end=time.monotonic()+900
 for n in range(1,62):
  p=k/('lease-attempt%d-console.txt'%n)
  with p.open('x') as f:
   child=subprocess.Popen(['pwsh','-NoProfile','-File',str(k/'Build.ps1')],stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
   r.update(status='owned_build_or_preflight',pid=child.pid);save();code=child.wait()
  text=p.read_text();busy="Xbox resource 'build' is busy or unavailable" in text
  r['attempts'].append(dict(attempt=n,exit_code=code,resource_busy=busy,log_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat()));save()
  if not busy:
   assert code==0,'Build failure is preserved, never repeat source/output creation'
   r.update(status='compiled',closed=True);save();break
  assert not (k/'build001.json').exists() and not (k/'artifacts/build001').exists(),'Refusal after output creation is not retryable'
  assert time.monotonic()<end,'Lease wait deadline, no build started'
  time.sleep(15)
 else:raise RuntimeError('Bound exhausted')
except Exception as e:r.update(status='preserved_failure',error=repr(e));save();raise
finally:r.update(closed=True);save()
print(json.dumps(r,indent=2))
