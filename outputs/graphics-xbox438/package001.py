"""Prepare exact physical control inputs, without uploading or executing them."""
import hashlib,json,py_compile,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=W/'work/graphics438'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not P.exists() and not (K/'package001.json').exists()
build=json.loads((K/'build001.json').read_text());assert build['exit_code']==0
assert json.loads((K/'binary-review001.json').read_text())['passed']
old=(K.parent/'graphics-nt5437/runner.c').read_text()
expected=old.replace('Owned NT5 fixture only','Owned physical Xbox Windows fixture only').replace('437','438').replace('A:\\\\LADDER.EXE','C:\\\\xwn438-kit\\\\ladder.exe')
assert (K/'runner.c').read_text()==expected
assert json.loads((K.parent/'graphics-nt5437/runtime-review002.json').read_text())['all_allowed_cases_passed']
sources=[Path('//wsl.localhost/Ubuntu/home/paul/xbox-windows-native/graphics438-build001/run438.exe'),Path('E:/xwn436/build004/ladder.exe')]
P.mkdir();(P/'payload').mkdir();files={}
for path,row in zip(sources,build['rows']):
 assert sha(path)==row['sha256'];dest=P/'payload'/path.name;dest.write_bytes(path.read_bytes());assert sha(dest)==row['sha256']
 files[path.name]=dict(path=str(dest),bytes=dest.stat().st_size,sha256=sha(dest))
dependencies=list(K.glob('*.py'))+[K/'runner.c']+[W/p for p in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','tools/graphics_sample.py']]
pins={str(p):sha(p) for p in dependencies}
for p in K.glob('*.py'):compile(p.read_bytes(),str(p),'exec')
r=dict(passed=True,files=files,dependencies=pins,runner_change='Only fixture ID, schema and source-copy path versus the actual NT5 runner',sample_unchanged=True,uploaded=False,guest_launched=False,driver_or_mode_change=False)
(K/'package001.json').write_text(json.dumps(r,indent=2)+'\n');print('Physical test package ready; no console writes or launch.')
