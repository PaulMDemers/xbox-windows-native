"""Freeze tested540 sources and exact bytes. No network or runtime execution."""
import ast,hashlib,json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'package001.json';assert not out.exists()
q=read(K/'prepared001.json');assert q['prepared']
r=read(K/'stack-host001.json');assert r['status']=='passed' and r['case_count']==40 and r['source_sha256']==sha(K/'stack_host.py')
r=read(K/'interval-review001.json');assert r['passed'] and r['source_sha256']==sha(K/'interval_review.py')
for name in ['host001.json','stage-host002.json']:
    r=read(K/name);assert r['passed'] and r['source_sha256']==sha(K/'controller.py')
for name,row in read(K/'workflow-copy001.json')['files'].items():
    assert sha(Path(row['source']))==row['source_sha256']
    assert sha(K/name)==row['sha256']
for p in K.glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
for row in q['images'].values():assert sha(Path(row['path']))==row['sha256']
assert read(K.parent/'entry-footprint539/audit1.json')['hives_clean']
assert read(K.parent/'entry-footprint539/after1.json')['completed']
pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()};pins.update(q['pins'])
for rel in ['outputs/entry-footprint539/after1.json','outputs/entry-footprint539/audit1.json',
 'outputs/cold-pair534/controller.py','outputs/cold-pair534/preflight001.json',
 'outputs/windows-pair532/controller.py','outputs/visible-dispatch528/physical.py',
 'outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py',
 'outputs/surface-bridge260/atomic_json.py','outputs/cpu-context489/decode.py',
 'outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py',
 'tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json']:
    p=W/rel;pins[str(p)]=sha(p)
for p,h in pins.items():assert sha(Path(p))==h,p
free=shutil.disk_usage('C:/').free;assert free-64*1024**2>=20*1024**3
r=dict(passed=True,pins=pins,images=q['images'],launches_allowed=1,C_free_bytes=free,projected_bytes=64*1024**2,
    E_host_allocation=0,no_hook=True,physical_access=False,compiled=False,
    stack_cases=40,controller_cases=19,stage_capture_cases=6,windows_boot_intended=False,
    intentional_indefinite_hold=True,manual_reset_required=True,watcher_required=True,
    scope='Existing post-stack LED marker then intentional stop. Not a Windows boot or a fix.')
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8',newline='\n');print('PASS frozen package',len(pins),'pins')
