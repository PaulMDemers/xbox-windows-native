"""Freeze801 only after fresh corrected bridge, CPU, memory and linked checks."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn801');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['page-boundary001.json','layout-independent001.json','link-review012.json','model003.json','model004.json','equivalence002.json','payload008.json','host007.json','host-plan006.json','cpu-build005.json','cpu-run005.json','integration010.json','optical-review001.json','build002.json','page-review002.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json','receipt-storage001.json']
for n in checks:assert read(n)['passed'],n
failures=['qualification-failure001.json','qualification-failure002.json','qualification-failure003.json','host004.json','integration008.json','integration009.json']
for n in failures:assert not read(n)['passed'],n
c=read('cpu-run005.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host007.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host007'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==19 and sum(v['type']=='R_386_32' for v in h['relocations'])==14
assert len(read('optical-schema001.json')['omitted_aggregate_masks'])==20
assert len(read('model004.json')['cases'])==854 and len(read('integration010.json')['cases'])==844
assert (K/'bridge003.S').read_text().count('0x8d8(%ebp)')==2
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':2680,'result_end':0x74b8,'zeroed_reserved_end':0x74b8,'stack_start':0x7d00,'stack_bytes':768,'payload_bytes':read('payload008.json')['unpadded_bytes'],'padded_payload_extent':23040,'relocations':19,'absolute_relocations':14,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':844,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'preserved_failures':{n:sha(K/n) for n in failures},'limits':['No physical result yet','Same-value CR02/NVVVALIDSTART/CR07total write/undo drops indistinguishable','Twenty masks omitted raw; final success requires all28','No later mode operations','Intentional hold; photo/reset required','Source bridge comment says 2KiB stack historically; actual verified stack is768bytes']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build012.py -> build002','active_host':'host_build009.py -> host007','active_payload':'payload_build008.py -> payload008 / probe-compact-native.c','active_bridge':'bridge003.S','active_cpu':'cpu005.py','active_integration':'integration012.py -> integration010','active_controller':'physical007.py','active_frontend_sources':{'main.c':'main004.c','layout.c':'layout004.c'},'active_source_review':'source_review005.py','superseded_not_admitted':['probe.c','probe-compact.c','payload007','host004','host005','host006','bridge002.S','model001','model002','integration008','integration009'],'source_generators_are_historical_only':True}
for n,obj in [('review001.json',r),('sources001.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS801 frozen pre-stage source review')
