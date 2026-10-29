"""Freeze804 only after fresh bridge, CPU, memory, controller and linked checks."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn804');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['page-boundary001.json','layout-independent001.json','link-review012.json','model001.json','model002.json','equivalence001.json','payload008.json','host007.json','host-plan006.json','cpu-build005.json','cpu-run005.json','integration010.json','optical-review001.json','build002.json','page-review002.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json','receipt-storage001.json','controller-review001.json']
for n in checks:assert read(n)['passed'],n
c=read('cpu-run005.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host007.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host007'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==22 and sum(v['type']=='R_386_32' for v in h['relocations'])==15
assert len(read('optical-schema001.json')['omitted_aggregate_masks'])==21
assert len(read('model002.json')['cases'])==894 and len(read('integration010.json')['cases'])==884
assert (K/'bridge003.S').read_text().count('0x8d8(%ebp)')==2
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':2800,'result_end':0x73b0,'zeroed_reserved_end':0x73b0,'stack_start':0x7d00,'stack_bytes':768,'payload_bytes':read('payload008.json')['unpadded_bytes'],'padded_payload_extent':22656,'relocations':22,'absolute_relocations':15,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':884,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','Same-value CR02/NVVVALIDSTART/CR07total write/undo drops indistinguishable','Twenty-one masks omitted raw; final success requires all29','No later mode operations','Intentional hold; photo/reset required','link-review012 historical required_execution_checks label model004 is superseded by actual model002 in this gate']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build012.py -> build002','active_host':'host_build009.py -> host007','active_payload':'payload_build008.py -> payload008 / probe-shared-native.c','active_bridge':'bridge003.S','active_cpu':'cpu005.py','active_integration':'integration012.py -> integration010','active_controller':'physical008.py','active_frontend_sources':{'main.c':'main004.c','layout.c':'layout004.c'},'active_source_review':'source_review001.py','not_admitted':['physical007.py','probe-native.c','probe-compact-native.c','probe-shared-read-native.c','measure001','measure002'],'source_generators_are_historical_only':True}
for n,obj in [('review001.json',r),('sources001.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS804 frozen pre-stage source review')
