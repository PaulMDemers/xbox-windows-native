"""Freeze789 only after fresh native instructions, memory layout and linked frontend validation."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn789');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['page-boundary001.json','layout-independent001.json','link-review008.json','model001.json','payload005.json','host003.json','host-plan002.json','cpu-build002.json','cpu-run002.json','integration005.json','optical-review001.json','build002.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert read(n)['passed'],n
c=read('cpu-run002.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host003.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host003'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==18 and sum(v['type']=='R_386_32' for v in h['relocations'])==13
assert len(read('optical-schema001.json')['omitted_aggregate_masks'])==14
assert len(read('model001.json')['cases'])==614 and len(read('integration005.json')['cases'])==604
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':1960,'result_end':0x5fe8,'zeroed_reserved_end':0x5fe8,'stack_start':0x6800,'payload_bytes':read('payload005.json')['unpadded_bytes'],'padded_payload_extent':18432,'relocations':18,'absolute_relocations':13,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':604,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','Same-value CR02/NVVVALIDSTART write/undo drops indistinguishable','Fourteen masks omitted raw; final success requires all22','CR10 diagnostic only; no later mode operations','Intentional hold; photo/reset required']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build007.py -> build002','active_host':'host_build005.py -> host003','active_cpu':'cpu002.py','active_integration':'integration007.py -> integration005','active_controller':'physical004.py','active_frontend_sources':{'main.c':'main004.c','layout.c':'layout004.c'},'active_source_review':'source_review002.py','active_page_reviews':['page_review004.py','page_boundary005.py'],'historical_generators_only':['prepare.py','extend_integration.py'],'rejected_or_superseded':['main.c','layout.c','integration005.py','integration006.py','build006.py','source_review.py','review_prepare.py','physical003.py','audit_collection006.py','page_review003.py','page_boundary004.py','link_review007.py']}
for n,obj in [('review001.json',r),('sources001.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS789 frozen source pre-stage review')
