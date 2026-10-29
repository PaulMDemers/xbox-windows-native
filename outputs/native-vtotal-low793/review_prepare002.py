"""Freeze793 only after fresh native instruction/layout/link qualification."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn793');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['link-reference-correction001.json','page-boundary001.json','layout-independent001.json','link-review008.json','model001.json','payload005.json','host003.json','host-plan002.json','cpu-build002.json','cpu-run002.json','integration006.json','optical-review001.json','build002.json','page-review002.json','plan-review001.json','linked-review001.json','source-review002.json','optical-schema001.json']
for n in checks:assert read(n)['passed'],n
c=read('cpu-run002.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host003.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host003'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==18 and sum(v['type']=='R_386_32' for v in h['relocations'])==13
assert len(read('optical-schema001.json')['omitted_aggregate_masks'])==16
assert len(read('model001.json')['cases'])==694 and len(read('integration006.json')['cases'])==684
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':2200,'result_end':0x68d8,'zeroed_reserved_end':0x68d8,'stack_start':0x7800,'payload_bytes':read('payload005.json')['unpadded_bytes'],'padded_payload_extent':20480,'relocations':18,'absolute_relocations':13,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':684,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','Same-value CR02/NVVVALIDSTART/CR07total write/undo drops indistinguishable','Sixteen masks omitted raw; final success requires all24','No CR16/later mode operations','Intentional hold; photo/reset required']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build008.py -> build002','active_host':'host_build005.py -> host003','active_cpu':'cpu002.py','active_integration':'integration008.py -> integration006','active_controller':'physical005.py','active_frontend_sources':{'main.c':'main004.c','layout.c':'layout004.c'},'active_source_review':'source_review002.py','historical_generators_only':['prepare.py','extend_integration.py']}
for n,obj in [('review002.json',r),('sources002.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS793 frozen pre-stage source review')
