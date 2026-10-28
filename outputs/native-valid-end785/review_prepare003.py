"""Freeze785 only after fresh native and linked frontend validation."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent;P=Path('C:/xwn785');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
checks=['layout-independent001.json','link-review007.json','model001.json','payload005.json','host002.json','host-plan001.json','cpu-build001.json','cpu-run001.json','integration004.json','optical-review001.json','build002.json','page-review001.json','plan-review001.json','linked-review001.json','source-review001.json','optical-schema001.json']
for n in checks:assert read(n)['passed'],n
c=read('cpu-run001.json');assert c['closed'] and len(c['cases'])==12 and all(v['closed'] for v in c['cases'])
h=read('host002.json')
for n,v in h['sources'].items():assert sha(K/n)==v,n
for n,v in h['files'].items():assert sha(P/'host002'/n)==v,n
for n,v in read('build002.json')['files'].items():assert sha(P/'build002'/n)==v['sha256'],n
assert len(h['relocations'])==18 and sum(v['type']=='R_386_32' for v in h['relocations'])==13
assert read('optical-schema001.json')['omitted_aggregate_masks']==['CR00','CR02','CR03','secondCR05','firstCR17','CR01','secondCR02','secondCR17','secondCR19','CR13','NVVVALIDSTART','NVVSYNCSTART']
r={'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'result_bytes':1720,'result_end':0x57b8,'zeroed_reserved_end':0x57b8,'stack_start':0x6000,'payload_bytes':read('payload005.json')['unpadded_bytes'],'padded_payload_extent':15360,'relocations':18,'absolute_relocations':13,'CPU_cases':12,'all_CPU_closed':True,'integration_cases':526,'optical_cases':len(read('optical-review001.json')['cases']),'physical_access':False,'limits':['No physical result yet','Same-value CR02/NVVVALIDSTART write/undo drops indistinguishable','Twelve masks omitted raw; final success requires all20','NVVVALIDEND diagnostic only; no later mode operations','Intentional hold; photo/reset required']}
sources={'files':{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.py','.c','.h','.S','.ld'] or p.name in ['Makefile','.gitattributes']},'active_build':'build006.py -> build002','active_host':'host_build005.py -> host002','active_cpu':'cpu002.py','active_integration':'integration005.py -> integration004','active_controller':'physical003.py','historical_generators_only':['prepare.py','extend_integration.py','prepare_reviews.py']}
for n,obj in [('review001.json',r),('sources001.json',sources)]:
 assert not (K/n).exists();(K/n).write_text(json.dumps(obj,indent=2)+'\n')
print('PASS785 frozen source pre-stage review')
