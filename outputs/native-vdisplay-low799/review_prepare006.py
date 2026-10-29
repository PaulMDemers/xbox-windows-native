"""Freeze799 only after fresh corrected bridge, CPU, memory and link checks."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn799');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['page-boundary001.json','layout-independent001.json','link-review010.json','model001.json','payload007.json','host004.json','host-plan003.json','cpu-build003.json','cpu-run003.json','integration008.json','optical-review001.json','build002.json','page-review002.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert read(n)['passed'],n
assert not read('payload006.json')['passed']
assert all(not read(n)['passed'] for n in ['qualification-failure001.json'])
c=read('cpu-run003.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host004.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host004'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==18 and sum(v['type']=='R_386_32' for v in h['relocations'])==13
assert len(read('optical-schema001.json')['omitted_aggregate_masks'])==19
assert len(read('model001.json')['cases'])==814 and len(read('integration008.json')['cases'])==804
assert (K/'bridge002.S').read_text().count('0x8d8(%ebp)')==2
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':2560,'result_end':0x75c0,'zeroed_reserved_end':0x75c0,'stack_start':0x7e00,'payload_bytes':read('payload007.json')['unpadded_bytes'],'padded_payload_extent':23424,'relocations':18,'absolute_relocations':13,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':804,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'preserved_failures':{n:sha(K/n) for n in ['qualification-failure001.json']},'limits':['No physical result yet','Same-value CR02/NVVVALIDSTART/CR07total write/undo drops indistinguishable','Nineteen masks omitted raw; final success requires all27','No later mode operations','Intentional hold; photo/reset required']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build010.py -> build002','active_host':'host_build006.py -> host004','active_bridge':'bridge002.S','active_cpu':'cpu003.py','active_integration':'integration010.py -> integration008','active_controller':'physical007.py','active_frontend_sources':{'main.c':'main004.c','layout.c':'layout004.c'},'active_source_review':'source_review004.py','historical_generators_only':['prepare.py','extend_integration.py','revise_layout001.py']}
for n,obj in [('review001.json',r),('sources001.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS799 frozen pre-stage source review')
