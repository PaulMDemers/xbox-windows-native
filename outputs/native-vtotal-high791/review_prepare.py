"""Freeze791 only after fresh native instruction/layout/link qualification."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn791');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['page-boundary001.json','layout-independent001.json','link-review008.json','model001.json','payload005.json','host003.json','host-plan002.json','cpu-build002.json','cpu-run002.json','integration005.json','optical-review001.json','build002.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert read(n)['passed'],n
c=read('cpu-run002.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host003.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host003'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==18 and sum(v['type']=='R_386_32' for v in h['relocations'])==13
assert len(read('optical-schema001.json')['omitted_aggregate_masks'])==15
assert len(read('model001.json')['cases'])==654 and len(read('integration005.json')['cases'])==644
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':2080,'result_end':0x6460,'zeroed_reserved_end':0x6460,'stack_start':0x7000,'payload_bytes':read('payload005.json')['unpadded_bytes'],'padded_payload_extent':19456,'relocations':18,'absolute_relocations':13,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':644,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','Same-value CR02/NVVVALIDSTART/CR07total write/undo drops indistinguishable','Fifteen masks omitted raw; final success requires all23','No CR06/CR16/later mode operations','Intentional hold; photo/reset required']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build007.py -> build002','active_host':'host_build005.py -> host003','active_cpu':'cpu002.py','active_integration':'integration007.py -> integration005','active_controller':'physical004.py','active_frontend_sources':{'main.c':'main004.c','layout.c':'layout004.c'},'active_source_review':'source_review.py','historical_generators_only':['prepare.py','extend_integration.py']}
for n,obj in [('review001.json',r),('sources001.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS791 frozen pre-stage source review')
