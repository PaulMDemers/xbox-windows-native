"""Verify exact four-operand change and immutable host outputs; no rerun."""
import hashlib,json,struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'final-review.json';assert not out.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
h=json.loads((K/'host001.json').read_text());assert h['status']=='passed' and h['actual_cases']==51
s=(K/'marker.S').read_text();assert s.count('test eax, 0xfffff7e7')==2 and s.count('test eax, 0x808')==2
assert s.replace('test eax, 0xfffff7e7','test eax, 0xfffff7ef').replace('test eax, 0x808','test eax, 0x800')==(K.parent/'entry-marker465/marker.S').read_text()
for path,v in h['files'].items():assert sha(Path(path.replace('/mnt/c/','C:/')))==v['sha256']
for n in [32,33,34,35,36,37,49,50]:
 r=struct.unpack('<24I',Path(f'C:/xwn470/host001/case{n:02d}.bin').read_bytes());assert r[5:8]==(1,2,3)
for n in [42,43,44,45,46]:
 r=struct.unpack('<24I',Path(f'C:/xwn470/host001/case{n:02d}.bin').read_bytes());assert r[5]==5 and r[6]==0
out.write_text(json.dumps(dict(passed=True,host_only=True,actual_assembled_cases=51,immutable_repeats=51,
 four_operand_change_only=True,physical_469_prefix_represented_with_modeled_future_completion=True,
 hardware_completion_not_proved=True,XBE_built=False,physical_access=False,renderer_or_driver_changed=False,
 privileged_interfaces='MODELED',private_files_verified=len(h['files'])),indent=2)+'\n')
