"""Longer bounded retry of unchanged repository scan after001 timed out."""
import json,subprocess,sys,time
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'repository-check002.json';assert not out.exists()
started=time.monotonic();r=dict(passed=False,timeout_seconds=600,checker_unchanged=True,prior_timeout_preserved=True)
try:
    p=subprocess.run([sys.executable,'-B',str(W/'tools/check-repository.py')],cwd=W,capture_output=True,text=True,timeout=600)
    r.update(exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr,passed=p.returncode==0)
except subprocess.TimeoutExpired as e:r.update(timeout=True,stdout=(e.stdout or b'').decode() if isinstance(e.stdout,bytes) else e.stdout,stderr=(e.stderr or b'').decode() if isinstance(e.stderr,bytes) else e.stderr)
finally:
    r['elapsed_seconds']=time.monotonic()-started;out.write_text(json.dumps(r,indent=2)+'\n')
assert r['passed'],r;print(r['stdout'].strip())
