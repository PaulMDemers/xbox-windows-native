"""Freeze reviewed490 diagnostic and unchanged486 arithmetic workload."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'package001.json';assert not out.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(K/'build001.json');full=read(K/'full-host002.json');control=read(K/'controller-host001.json')
assert b['status']=='compiled' and full['status']=='passed' and full['cases']==154
assert control['passed'] and len(control['cases'])==17 and control['source_sha256']==sha(K/'physical.py')
for n in ['validation001.json','full-transport002.json','imports001.json']:assert read(K/n)['passed']
assert read(K.parent/'blend-precision486/final-review.json')['arithmetic_characterization_passed']
for r in [b,full,read(K/'runner-build001.json')]:
 for n,v in r['files'].items():
  p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'],n
modules={}
for row in read(K.parent/'blend-precision486/module-review001.json')['rows']:
 for m in row['modules']:
  if m['path'].startswith('winnt/system32/'):
   n=m['path'].rsplit('/',1)[-1]
   if n in modules:assert modules[n]==m['sha256']
   modules[n]=m['sha256']
assert len(modules)==10
files={}
for n in ['default.xbe','run490.exe','d3d.exe']:
 p=Path('C:/xwn490')/('build001' if n=='default.xbe' else 'runner-build001')/n
 files[n]=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
assert files['d3d.exe']['sha256']=='e7942c5ba903195dbafcfd379caa9a28ba335e9e52901b139263572c7ac6cec1'
deps=list(K.glob('*.py'))+list(K.glob('*.c'))+[K/n for n in ['DESIGN.md','context.S','build001.json','validation001.json','host-run001.json','full-host002.json','full-transport002.json','controller-host001.json','runner-build001.json','imports001.json']]+[W/n for n in ['outputs/cpu-context489/decode.py','outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','outputs/blend-precision486/graphics_precision.py','tools/graphics_discovery.py','outputs/blend-precision486/precision.c','outputs/blend-precision486/final-review.json','outputs/blend-precision486/runtime-review001.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py']]
for p in K.glob('*.py'):ast.parse(p.read_text())
out.write_text(json.dumps(dict(passed=True,files=files,dependencies={str(p.resolve()):sha(p) for p in deps},runtime_module_pins=modules,physical_access=False,full_wrapper_cases=154,privileged_fixture_cases=46,controller_cases=17,sample_byte_identical_to_PC=True,context_scope='registers only; no page walk or own-close attestation'),indent=2)+'\n')
print(json.dumps(dict(passed=True,dependencies=len(deps),files=files)))
