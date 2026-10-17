"""Prelaunch independent-oracle model controls; no guest execution."""
import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'controls001.json';assert not out.exists()
r=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(W/'tests'),'-p','test_graphics_present.py'],capture_output=True,text=True,timeout=90)
record=dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,passed=r.returncode==0,
 scope='Independent host oracle model tests only, no runtime presentation result',
 files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [W/'tools/graphics_present.py',W/'tests/test_graphics_present.py']})
out.write_text(json.dumps(record,indent=2)+'\n');assert r.returncode==0
print('Presentation oracle controls passed.')
