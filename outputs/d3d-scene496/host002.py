import hashlib,json,shutil,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn496/host002')
assert not P.exists();P.mkdir(parents=True)
paths=['tests/test_graphics_scene.py','tools/graphics_scene.py','tools/graphics_scene_oracle.py','tools/graphics_depth.py','tools/graphics_texture.py','tools/graphics_discovery.py','tools/graphics_d3dpresent.py']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(W/'tools/graphics_scene_oracle.py')=='38f38f6e3393e34734c5c008cf5037b0f3d48badd2f813e15f4893eb66548832'
for n in paths:shutil.copyfile(W/n,P/Path(n).name)
with (P/'tests.log').open('xb') as f:r=subprocess.run([sys.executable,'-B',str(P/'test_graphics_scene.py'),'-v'],stdout=f,stderr=subprocess.STDOUT,timeout=180)
record=dict(passed=r.returncode==0,exit_code=r.returncode,scope='Synthetic host metadata/COM and pixel streams only; no guest',files=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in sorted(P.iterdir())])
(K/'oracle-tests002.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print((P/'tests.log').read_text());assert r.returncode==0
