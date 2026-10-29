"""Freeze811 host qualification; the controller separately requires cold810 PASS."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn811');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['compaction-review001.json','page-boundary001.json','layout-independent001.json','link-review012.json','model001.json','model002.json','equivalence001.json','payload008.json','host007.json','host-plan006.json','cpu-build006.json','cpu-run006.json','integration012.json','optical-review001.json','build002.json','page-review002.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json','receipt-storage001.json','controller-review001.json']
for n in checks:assert read(n)['passed'],n
c=read('cpu-run006.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host007.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host007'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==42 and sum(v['type']=='R_386_32' for v in h['relocations'])==34
assert len(read('optical-schema001.json')['omitted_aggregate_masks'])==24
assert len(read('model002.json')['cases'])==1014 and len(read('integration012.json')['cases'])==1004
assert (K/'bridge003.S').read_text().count('0x8d8(%ebp)')==2
assert not read('integration010.json')['passed'] and not read('integration011.json')['passed']
assert "audit['raw_result'][0]==0x810" in (K/'physical009.py').read_text()
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':3160,'result_end':0x7458,'stack_start':0x7d00,'stack_bytes':768,'payload_start':0x900,'payload_bytes':read('payload008.json')['unpadded_bytes'],'padded_payload_extent':24256,'relocations':42,'absolute_relocations':34,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':1004,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'hardware_admission':False,'hardware_gate':'Cold810 closed physical PASS and raw result0x810 required by controller.verify before stage or launch','limits':['No physical result yet','Same-value CR09 linecompare write/undo drops indistinguishable','24 masks omitted raw; final success requires all32','No later mode operations or Windows proof','Intentional hold; photo/reset required','Compaction preserves modeled device trace; physical timing equivalence unproved','Failed integration010/011 retained; corrected integration014 used']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build014.py -> build002','active_host':'host_build009.py -> host007','active_payload':'payload_build008.py -> payload008 / probe-pairs-native.c','active_bridge':'bridge003.S','active_cpu':'cpu006.py','active_integration':'integration014.py -> integration012','active_controller':'physical009.py','active_frontend_sources':{'main.c':'main004.c','layout.c':'layout004.c'},'active_source_review':'source_review001.py','not_admitted':['probe-native.c','probe-compact-native.c','probe-shared-native.c','probe-bitmap-native.c','measure001','measure002','measure003','integration012.py','integration013.py','build013.py'],'source_generators_are_historical_only':True}
for n,obj in [('review001.json',r),('sources001.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS811 host qualification frozen; no hardware admission until cold810 PASS')
