"""Freeze the qualified PC texture, corrected diagnostic and physical controller."""
import ast,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'package001.json';assert not out.exists()
sys.path.insert(0,str(K));from decode import decode;from witness_decode import decode_refusal
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
b=read(K/'build001.json');h=read(K/'host002.json');assert b['status']=='compiled' and h['status']=='passed' and h['cases']==132
assert read(K/'binary-review001.json')['passed'] and read(K/'controller-host001.json')['passed']
assert read(K.parent/'blend-precision486/final-review.json')['arithmetic_characterization_passed']
assert read(K/'imports001.json')['passed'] and read(K/'transport001.json')['status']=='passed'
for r in [b,h,read(K/'runner-build001.json')]:
 for n,v in r['files'].items():
  p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'],n
assert read(K/'controller-host001.json')['source_sha256']==sha(K/'physical.py')
original=(K.parent/'blend-precision486/runner.c').read_text();actual=(K/'runner.c').read_text()
assert actual.replace('487','486').replace('Owned physical Xbox Windows fixture only','Owned NT5 PC fixture only').replace('C:'+chr(92)*2+'xwn486-kit'+chr(92)*2+'d3d.exe','A:'+chr(92)*2+'D3D.EXE')==original
accepted=rejected=0
for pattern,size,fn in [('case*.bin',176,decode),('refusal*.bin',192,decode_refusal)]:
 for p in Path('C:/xwn487/host002').glob(pattern):
  data=p.read_bytes()
  if len(data)==size:fn(data);accepted+=1
  else:
   try:fn(data)
   except ValueError:rejected+=1
   else:raise AssertionError(p)
modules={}
for row in read(K.parent/'blend-precision486/module-review001.json')['rows']:
 for m in row['modules']:
  if m['path'].startswith('winnt/system32/'):
   name=m['path'].rsplit('/',1)[-1]
   if name in modules:assert modules[name]==m['sha256']
   modules[name]=m['sha256']
assert len(modules)==10
files={}
for n in ['default.xbe','run487.exe','d3d.exe']:
 p=Path('C:/xwn487')/('build001' if n=='default.xbe' else 'runner-build001')/n
 files[n]=dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
assert files['d3d.exe']['sha256']=='e7942c5ba903195dbafcfd379caa9a28ba335e9e52901b139263572c7ac6cec1'
deps=list(K.glob('*.py'))+list(K.glob('*.c'))+[K/n for n in ['DESIGN.md','witness.S','build001.json','binary-review001.json','host002.json','controller-host001.json','transport001.json','runner-build001.json','imports001.json']]+[W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','outputs/blend-precision486/graphics_precision.py','tools/graphics_discovery.py','outputs/blend-precision486/precision.c','outputs/blend-precision486/final-review.json','outputs/blend-precision486/runtime-review001.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py']]
for p in K.glob('*.py'):ast.parse(p.read_text())
out.write_text(json.dumps(dict(passed=True,files=files,dependencies={str(p):sha(p) for p in deps},runtime_module_pins=modules,decoded_host_files=accepted,truncated_host_files_rejected=rejected,controller_original_reconstructed=True,sample_byte_identical_to_PC=True,physical_access=False),indent=2)+'\n');print(json.dumps(dict(passed=True,dependencies=len(deps),decoded=accepted,rejected=rejected,boot_sha256=b['sha256'])))
