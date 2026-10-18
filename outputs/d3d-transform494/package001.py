"""Freeze exact matched sample, path-only launcher and actual dispatcher tests."""
import ast,hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'package001.json';assert not out.exists()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(K/'build002.json');control=read(K/'controller-host001.json')
assert b['status']=='compiled' and b['full_expected_binary_match'] and b['diagnostic_schema']==490
assert control['passed'] and len(control['cases'])==17 and control['source_sha256']==sha(K/'physical.py')
assert read(K/'imports001.json')['passed']
assert read(K.parent/'d3d-transform493/runtime-review002.json')['all_allowed_cases_passed']
for r in [b,read(K/'runner-build001.json')]:
 for n,v in r['files'].items():
  p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'],n
modules=read(K.parent/'context-adapter490/package001.json')['runtime_module_pins'];assert len(modules)==10
files={}
for n in ['default.xbe','run494.exe','d3d.exe']:
 p=Path('C:/xwn494')/('build002' if n=='default.xbe' else 'runner-build001')/n
 files[n]=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
assert files['d3d.exe']['sha256']=='02b6e4191b07eaccfe1dc199655a9deb1292e6e45341bf2a72c56fd2b25f8eca'
assert sha(W/'tools/graphics_transform.py')=='861c83730edbed0c2a3329d5961361fdaaa81eeaa5cf2b48e1dce51adff8128c'
deps=list(K.glob('*.py'))+list(K.glob('*.c'))+[K/n for n in ['DESIGN.md','build002.json','controller-host001.json','runner-build001.json','imports001.json']]+[W/n for n in ['outputs/cpu-context489/decode.py','outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','tools/graphics_transform.py','tools/graphics_discovery.py','tools/graphics_d3dpresent.py','src/samples/graphics-ladder/transform.c','outputs/d3d-transform493/final-review.json','outputs/d3d-transform493/runtime-review002.json','outputs/d3d-transform493/oracle-tests003.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py','outputs/context-adapter490/build001.json','outputs/context-adapter490/full-host002.json','outputs/context-adapter490/full-transport002.json','outputs/context-adapter490/package001.json']]
for p in K.glob('*.py'):ast.parse(p.read_text())
out.write_text(json.dumps(dict(passed=True,files=files,dependencies={str(p.resolve()):sha(p) for p in deps},runtime_module_pins=modules,physical_access=False,diagnostic_schema=490,attempt=494,controller_cases=17,sample_byte_identical_to_PC=True,inherited_host_tests='490 exact code; not new physical qualification',context_scope='registers only; no page walk or own-close attestation'),indent=2)+'\n')
print(json.dumps(dict(passed=True,dependencies=len(deps),files=files)))
