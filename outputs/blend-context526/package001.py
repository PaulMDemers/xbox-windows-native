"""Freeze the reviewed new arithmetic package before any network operation."""
import ast,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'package001.json';assert not out.exists()
js=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert js(K/'build-supervisor001.json')['passed'] and js(K/'review-build001.json')['passed']
assert js(K/'controller-host002.json')['source_sha256']==sha(K/'physical.py')
assert js(K/'imports001.json')['passed'] and js(K/'supervisor-host001.json')['passed']
assert js(K.parent/'blend-precision486/final-review.json')['arithmetic_characterization_passed']
files={}
for n in ['default.xbe','run526.exe','d3d.exe']:
 p=Path('C:/xwn526')/('build002' if n=='default.xbe' else 'runner-build001')/n
 files[n]=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
assert files['default.xbe']['sha256']=='407f631524dd5d264e5134a611327b9d3f9a6d2d135e94e45e4813c6a10c9a79'
assert files['d3d.exe']['sha256']=='e7942c5ba903195dbafcfd379caa9a28ba335e9e52901b139263572c7ac6cec1'
modules={}
for row in js(K.parent/'blend-precision486/module-review001.json')['rows']:
 for m in row['modules']:
  if m['path'].startswith('winnt/system32/'):
   n=m['path'].rsplit('/',1)[-1]
   if n in modules:assert modules[n]==m['sha256']
   modules[n]=m['sha256']
assert len(modules)==10
extra=['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','outputs/native-windows-physical-f/physical-cache-preflight.json','outputs/device-hardware220/state/demo251-claimed.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py','outputs/blend-precision486/graphics_precision.py','outputs/blend-precision486/precision.c','outputs/blend-precision486/final-review.json','outputs/blend-precision486/module-review001.json','tools/graphics_discovery.py','tools/graphics_blend.py','tools/graphics_depth.py','tools/graphics_texture.py','tools/graphics_d3d.py','outputs/cpu-context489/decode.py','outputs/context-adapter490/full-host002.json','outputs/context-adapter490/full-transport002.json','outputs/d3d-transform494/build002.json','outputs/d3d-transform494/physical-final001.json']
# Only existing dependencies are admitted; a missing required helper is an error.
deps=[p for p in K.iterdir() if p.is_file()]+[W/n for n in extra]
for p in K.glob('*.py'):ast.parse(p.read_text())
free={d:shutil.disk_usage(d+':/').free for d in ['C','E']};assert free['C']-64*1024**2>=20*1024**3
r=dict(passed=True,files=files,dependencies={str(p.resolve()):sha(p) for p in deps},runtime_module_pins=modules,physical_access=False,diagnostic_schema=490,attempt=526,controller_cases=17,sample_byte_identical_to_PC=True,inherited_host_tests='490/494 exact code; no new boot qualification',context_scope='registers only; no pagewalk or own-close proof',capacity_free_bytes=free)
out.write_bytes((json.dumps(r,indent=2)+'\n').encode());print('PASS',len(r['dependencies']),'pinned package dependencies')
