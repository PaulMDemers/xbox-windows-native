"""Preserve failed framebuffer check and correct only report pixel origin."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent
s=(K/'bridge002.S').read_text();assert s.count('add $768,%edi')==1
(K/'bridge003.S').write_bytes(s.replace('add $768,%edi','add $512,%edi').encode())
changes={
 'host_build009.py':('host_build008.py',{'host006':'host007','bridge002.S':'bridge003.S','plan_test003':'plan_test004'}),
 'plan_test004.py':('plan_test003.py',{'host-plan005':'host-plan006'}),
 'integration012.py':('integration011.py',{'host006':'host007','integration009':'integration010'}),
 'cpu005.py':('cpu004.py',{'host006':'host007','cpu004':'cpu005','cpu-build004':'cpu-build005','cpu-run004':'cpu-run005'}),
 'optical_review005.py':('optical_review004.py',{'host006':'host007'}),
 'build012.py':('build011.py',{'host006':'host007','cpu-run004':'cpu-run005','integration009':'integration010'}),
 'linked_review007.py':('linked_review006.py',{'host006':'host007'}),
 'page_review008.py':('page_review007.py',{'host006':'host007'}),
 'page_boundary009.py':('page_boundary008.py',{'host006':'host007'}),
}
for name,(old,mapping) in changes.items():
 p=K/name;assert not p.exists();s=(K/old).read_text()
 for a,b in mapping.items():s=s.replace(a,b)
 p.write_bytes(s.encode())
r={'passed':False,'physical_access':False,'receipt':'integration009.json','frozen_sources':'host006.json',
 'reason':'Full framebuffer oracle rejected shifted report squares. Layout generator replaced a 512-byte report pixel origin while increasing stack from 512 to 768 bytes.',
 'correction':'bridge003 changes only report pixel origin back to 512; stack remains 768 bytes. Fresh host007 and all downstream checks required.',
 'no_qualification_from_failed_attempt':True,'no_console_stage_or_launch':True}
(K/'qualification-failure003.json').write_text(json.dumps(r,indent=2)+'\n')
