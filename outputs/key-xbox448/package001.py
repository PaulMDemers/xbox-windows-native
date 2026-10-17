"""Package the exact qualified probe and physical controller; no console writes."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=W/'work/key-xbox448'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'package001.json';assert not out.exists() and not P.exists()
build=json.loads((K/'build001.json').read_text());assert build['exit_code']==0
assert json.loads((K/'binary-review001.json').read_text())['passed']
pc=K.parent/'key-depth447';review=json.loads((pc/'runtime-review001.json').read_text())
assert review['all_semantics_passed'] and review['mode_review']['passed']
assert json.loads((pc/'independent001.json').read_text())['passed']
assert json.loads((pc/'final-review.json').read_text())['semantics_passed']
old=(K.parent/'key-semantics446/runner.c').read_text(encoding='utf-8')
expected=old.replace('Owned NT5 fixture only','Owned physical Xbox Windows fixture only').replace('xwn446','xwn448').replace('number("schema",446)','number("schema",448)').replace('A:\\\\KEYPROBE.EXE','C:\\\\xwn448-kit\\\\keyprobe.exe')
assert (K/'runner.c').read_text(encoding='utf-8')==expected
P.mkdir();(P/'payload').mkdir();files={}
for row in build['rows']:
 name=Path(row['path']).name;dest=P/'payload'/name
 linux='/mnt/'+dest.drive[0].lower()+dest.as_posix()[2:]
 subprocess.run(['wsl','-d','Ubuntu','--','cp',row['path'],linux],check=True,timeout=45)
 assert sha(dest)==row['sha256'];files[name]=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest))
deps=list(K.glob('*.py'))+[K/'runner.c']+[W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','tools/graphics_keyprobe.py','src/samples/graphics-ladder/keyprobe.c']]
deps += [pc/n for n in ['runtime-review001.json','independent001.json','final-review.json']]
for p in K.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
record=dict(passed=True,files=files,dependencies={str(p):sha(p) for p in deps},sample_unchanged=True,
 runner_change='Only fixture ID/schema and source-copy path from actual446 controller; no desktop mode change',
 uploaded=False,guest_launched=False,driver_or_mode_change=False)
out.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print('Physical package ready, no console writes or launch.')
