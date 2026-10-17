"""Pin fresh lifecycle payloads and host dependencies before any console stage."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=W/'work/d3d-direct458';pc=K.parent/'d3d-discovery455'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'package001.json';assert not out.exists() and not P.exists()
b=json.loads((K/'build001.json').read_text());assert b['exit_code']==0 and json.loads((K/'binary-review001.json').read_text())['passed']
assert json.loads((pc/'final-review.json').read_text())['scoped_inventory_passed']
original=(pc/'runner.c').read_text();actual=(K/'runner.c').read_text()
assert actual.replace('458','455').replace('Owned physical Xbox Windows fixture only','Owned NT5 PC fixture only').replace('C:\\\\xwn455-kit\\\\d3d.exe','A:\\\\D3D.EXE')==original
P.mkdir();(P/'payload').mkdir();files={}
for row in b['rows']:
 name=Path(row['path']).name;dest=P/'payload'/name;linux='/mnt/'+dest.drive[0].lower()+dest.as_posix()[2:]
 subprocess.run(['wsl','-d','Ubuntu','--','cp',row['path'],linux],check=True,timeout=45);assert sha(dest)==row['sha256'];files[name]=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest))
deps=list(K.glob('*.py'))+[K/'runner.c']+[W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','tools/graphics_discovery.py','src/samples/graphics-ladder/discovery.c']]+[pc/n for n in ['runtime-review001.json','independent001.json','final-review.json']]
for p in K.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
out.write_text(json.dumps(dict(passed=True,files=files,dependencies={str(p):sha(p) for p in deps},sample_unchanged=True,controller_original_reconstructed=True,uploaded=False,guest_launched=False),indent=2)+'\n');print('Physical package pinned; no console writes.')
