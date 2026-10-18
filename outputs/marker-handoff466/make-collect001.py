import json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'cromwell-devices414'
b=json.loads((K/'build001.json').read_text())
for name in ['decode.py','refusal_decode.py']:
 s=(K.parent/'boot-refusal462'/name).read_text().replace('0x323634','0x363634').replace('0x46200101','0x46600101').replace('288316',str(b['payload_bytes']))
 if name=='refusal_decode.py':
  s=s.replace("11:'post-log low loader mismatch'","11:'post-log low loader mismatch',12:'bounded first marker refusal'")
  s=s.replace('if reason>=7 and','if 7<=reason<=11 and')
  s=s.replace(' return dict(record_complete='," if reason==12 and (r[5] not in (2,3,4,5,6,7) or r[6]!=0 or not r[8]):raise ValueError('Marker refusal state')\n return dict(record_complete=")
 (K/name).write_text(s)
s=(P/'collect.py').read_text().replace('/mnt/e/xwn414','/mnt/c/xwn466').replace('nt5-cromwell414-emu001','nt5-marker466-emu001')
s=s.replace("K.parent/'handoff-trace412/preparation002.json'","K/'preparation001.json'").replace("prep['fixture']","prep['seed']").replace("prep['fixture_sha256']","prep['seed_sha256']")
s=s.replace('from stock_io002 import scan','from stock_io002 import scan,readers\nfrom decode import decode')
anchor="scan(child,P/'allocation/artifacts');allocation=json.loads((P/'allocation/allocation.json').read_text())"
addition='''
with ColdIO(child) as io:
    w=readers(io,child)['E'];candidate=w.read('Applications/XWNBoot466a/default.xbe');primary=w.read('Applications/XWNBoot466a/report.bin')
    assert candidate==Path('/mnt/c/xwn466/build001/default.xbe').read_bytes()
    (P/'primary.bin').write_bytes(primary);decoded=decode(primary)
    assert decoded['preparation_verified']
'''
assert s.count(anchor)==1;s=s.replace(anchor,anchor+addition)
s=s.replace('r=dict(closed=True,','r=dict(candidate_exact=True,primary=decoded,closed=True,')
(K/'collect.py').write_text(s)
