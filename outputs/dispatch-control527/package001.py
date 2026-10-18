"""Freeze standalone application and scoped emulator qualification for one physical run."""
import ast,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'package001.json';assert not out.exists()
for n in ['host001','controller-host001','supervisor-host001','emu-audit002']:assert read(K/(n+'.json'))['passed']
h=read(K/'controller-host001.json');assert len(h['cases'])==30 and h['source_sha256']==sha(K/'physical.py')
h=read(K/'supervisor-host001.json');assert h['all_children_closed'] and h['source_sha256']==sha(K/'supervise.py')
a=read(K/'emu-audit002.json');assert a['actual_runtime_entry'] and a['begin_pipeline_completed'] and a['source_seed_unchanged']
assert a['closure']['closed'] and a['closure']['natural_exit'] and a['closure']['exit']==0 and not a['closure']['fallback']
assert a['after']['orphans']==0 and a['after']['errors']==0
build=read(K/'build001.json');assert build['compiled'] and build['sdk_unchanged']
p=Path('C:/xwn527/build001/bin/default.xbe');assert p.stat().st_size==102400
assert sha(p)==build['outputs']['bin\\default.xbe']['sha256']==read(K/'preparation002.json')['candidate_sha256']
pre=read(K/'prebuild001.json')
for n,h in pre['sources'].items():assert sha(K/n)==h and sha(Path('C:/xwn527/build001')/n)==h
for n,h in pre['tools'].items():assert sha(Path(n))==h
for n,h in pre['sdk'].items():assert sha(Path('C:/nxdk')/n)==h
old=(K.parent/'extent-physical525/physical.py').read_text();new=(K/'physical.py').read_text()
for start,end in [('def receipt(','def classify('),('def classify(','def stage('),('def cold_pair(','def collect(')]:assert old[old.index(start):old.index(end)]==new[new.index(start):new.index(end)]
assert 'put(f,HOOK' not in new and 'f.rename(' not in new
deps=list(K.glob('*.py'))+list(K.glob('*.c'))+list(K.glob('*.h'))+[K/n for n in ['Makefile','DESIGN.md','.gitattributes','host001.json','controller-host001.json','supervisor-host001.json','build001.json','prebuild001.json','preparation002.json','runtime-prepared002.json','emu-audit002.json','closure002.json']]
deps += [W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json','outputs/native-windows-physical-f/physical-cache-preflight.json','outputs/device-hardware220/state/demo251-claimed.json','outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py']]
for p in K.glob('*.py'):ast.parse(p.read_text())
free=shutil.disk_usage('C:/').free;assert free-64*1024**2>=20*1024**3
p=Path('C:/xwn527/build001/bin/default.xbe')
r=dict(passed=True,files={'default.xbe':dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))},dependencies={str(p.resolve()):sha(p) for p in deps},capacity_free_C=free,projected_C_bytes=64*1024**2,E_allocation=0,controller_cases=30,actual_supervisor_children=3,physical_access=False,
 scope='Standalone runtime/file receipt on exact emulator candidate; not Windows or whole-disk equality',emulator_disk_strict=False,emulator_changed_offset_outside_E=[1540],no_disk_gate_waiver=True)
out.write_text(json.dumps(r,indent=2)+'\n');print('PASS',len(r['dependencies']),'frozen inputs; standalone physical attempt ready')
