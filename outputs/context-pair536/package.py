"""Freeze tested preparation/controller sources before console access."""
from pathlib import Path
import ast,hashlib,json,shutil
K=Path(__file__).resolve().parent;W=K.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'package001.json';assert not out.exists()
for name in ['prepared001.json','host001.json','stage-host001.json','review001.json']:assert read(K/name)['passed']
for name in ['host001.json','stage-host001.json']:assert read(K/name)['source_sha256']==sha(K/'controller.py')
for row in read(K/'source-copy001.json'):
    p=Path(row['source']);b=p.read_bytes();assert sha(p)==row['source_sha256']
    expected=b.replace(b'534',b'536')
    if row['destination']=='supervise.py':expected=expected.replace(b'LIMITS=dict(before1=240,',b'LIMITS=dict(stage=240,before1=240,')
    assert (K/row['destination']).read_bytes()==expected
for p in K.glob('*.py'):ast.parse(p.read_text())
q=read(K/'prepared001.json');pins={str(p.resolve()):sha(p) for p in K.iterdir() if p.is_file()}
pins.update(q['pins'])
for rel in ['outputs/cold-pair534/controller.py','outputs/cold-pair534/preflight001.json',
            'outputs/windows-pair532/controller.py','outputs/visible-dispatch528/physical.py',
            'outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py',
            'outputs/surface-bridge260/atomic_json.py','outputs/cpu-context489/decode.py',
            'outputs/clean-media404/hive_audit004.py','outputs/native-windows-physical-f/decode-legacy-events.py',
            'tools/configure-e-display.py','tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json']:
    p=W/rel;pins[str(p)]=sha(p)
for p,h in pins.items():assert sha(Path(p))==h,p
free=shutil.disk_usage('C:/').free;assert free-64*1024**2>=20*1024**3
r=dict(passed=True,pins=pins,images=q['images'],controller_cases=29,stage_capture_cases=6,
       inherited_supervisor='534 byte-exact except536 namespace and stage240s action; no new child-lifetime implementation',
       compiled=False,diagnostic_instructions_unchanged=True,no_hook=True,C_free_bytes=free,
       projected_bytes=64*1024**2,E_host_allocation=0,physical_access=False)
out.write_text(json.dumps(r,indent=2)+'\n');print('PASS frozen package',len(pins),'pins')
