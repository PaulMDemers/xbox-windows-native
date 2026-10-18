"""Pin actual binaries, namespace-only sources, decoders and host dispatch checks."""
import ast,hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];out=K/'package001.json';assert not out.exists()
sys.path.insert(0,str(K));from decode import decode;from refusal_decode import decode_refusal
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text(encoding='utf-8'))
b=read(K/'build001.json');h=read(K/'host001.json');assert b['status']=='compiled' and h['status']=='passed' and h['cases']==104
assert read(K/'binary-review001.json')['passed'] and read(K/'controller-host001.json')['passed']
assert read(K.parent/'busy-handoff471/final-review.json')['passed'] and read(K.parent/'physical-busy472/final-review.json')['normal_windows_shutdown_event_proved']
for r in [b,h]:
 for n,v in r['files'].items():
  p=Path(n.replace('/mnt/c/','C:/'));assert sha(p)==v['sha256'] and p.stat().st_size==v['bytes'],n
assert read(K/'controller-host001.json')['source_sha256']==sha(K/'physical.py')
original=(K.parent/'d3d-discovery455/runner.c').read_text();actual=(K/'runner.c').read_text()
assert actual.replace('473','455').replace('Owned physical Xbox Windows fixture only','Owned NT5 PC fixture only').replace('C:\\\\xwn455-kit\\\\d3d.exe','A:\\\\D3D.EXE')==original
accepted=rejected=0
for pattern,size,fn in [('case*.bin',176,decode),('refusal*.bin',192,decode_refusal)]:
 for p in Path('C:/xwn473/host001').glob(pattern):
  data=p.read_bytes()
  if len(data)==size:fn(data);accepted+=1
  else:
   try:fn(data)
   except ValueError:rejected+=1
   else:raise AssertionError(p)
modules=read(W/'outputs/crypto-path425/modules001.json')['modules'];v=read(K.parent/'d3d-discovery455/independent001.json');assert v['passed'] and v['closed']
modules['ddraw.dll']=next(row['sha256'] for row in v['rows'] if row['path']=='winnt/system32/ddraw.dll')
modules={n:modules[n] for n in ['kernel32.dll','user32.dll','advapi32.dll','gdi32.dll','ddraw.dll']}
files={n:dict(path=str(Path('C:/xwn473/build001')/n),bytes=(Path('C:/xwn473/build001')/n).stat().st_size,sha256=sha(Path('C:/xwn473/build001')/n)) for n in ['default.xbe','run473.exe','d3d.exe']}
assert files['d3d.exe']['sha256']=='577bd78e1aae562eef1c7bc8c5d500f604e0d340fca50ea553504608dafdb143'
deps=list(K.glob('*.py'))+list(K.glob('*.c'))+[K/'build001.json',K/'binary-review001.json',K/'host001.json',K/'controller-host001.json']+[W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','tools/graphics_discovery.py','src/samples/graphics-ladder/discovery.c','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py']]
for p in K.glob('*.py'):ast.parse(p.read_text())
out.write_text(json.dumps(dict(passed=True,files=files,dependencies={str(p):sha(p) for p in deps},runtime_module_pins=modules,decoded_host_files=accepted,truncated_host_files_rejected=rejected,controller_original_reconstructed=True,sample_unchanged=True,physical_access=False),indent=2)+'\n');print(json.dumps(dict(passed=True,dependencies=len(deps),decoded=accepted,rejected=rejected,boot_sha256=b['sha256'])))
