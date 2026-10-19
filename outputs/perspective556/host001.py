import hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
out=K/'oracle-tests002.json';assert not out.exists()
r=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s','tests','-p','test_graphics_perspective*.py','-v'],cwd=W,capture_output=True,text=True,timeout=120)
paths=[W/n for n in ['tools/graphics_perspective.py','tools/graphics_perspective_oracle.py','tests/test_graphics_perspective.py','tests/test_graphics_perspective_oracle.py']]
out.write_text(json.dumps(dict(passed=r.returncode==0,stdout=r.stdout,stderr=r.stderr,files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},guest_qualification=False),indent=2)+'\n',encoding='utf-8')
print(r.stderr);assert r.returncode==0
