"""Preserve failed bridge build; create separately named corrected inputs."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def fresh(n,s):
 p=K/n;assert not p.exists(),n;p.write_bytes(s.encode())
e=json.loads((K/'integration006.json').read_text());assert not e['passed']
fresh('qualification-failure001.json',json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False,'stage':'full bridge integration006 first case','failure':'timer scratch changed from 0x8d8 to 0x950 by overbroad layout substitution; outside admitted writes 0x1ef0950','evidence':{n:sha(K/n) for n in ['host003.json','host-plan002.json','cpu-build002.json','integration006.json','bridge.S','prepare.py','lineage001.json']},'direct_model734_passed':True,'CPU002_fixtures_built_but_never_run':True,'optical_not_run':True,'physical_stage_or_launch':False,'owned_processes_remaining':False,'repair':'Fresh bridge002 keeps scratch at 0x8d8; page buffer zero length remains 0x950. Fresh host004, CPU003, integration007.'},indent=2)+'\n')
s=(K/'bridge.S').read_text();assert s.count('0x950(%ebp)')==2
fresh('bridge002.S',s.replace('0x950(%ebp)','0x8d8(%ebp)'))
for old,new,replacements in [
 ('plan_test.py','plan_test002.py',{'host-plan002.json':'host-plan003.json'}),
 ('host_build005.py','host_build006.py',{'host003':'host004',"K/'bridge.S'":"K/'bridge002.S'",'plan_test.py':'plan_test002.py'}),
 ('cpu002.py','cpu003.py',{'host003':'host004','cpu002':'cpu003','cpu-build002':'cpu-build003','cpu-run002':'cpu-run003'}),
 ('integration008.py','integration009.py',{'host003':'host004','integration006':'integration007'}),
 ('optical_review002.py','optical_review003.py',{'host003':'host004'}),
 ('build008.py','build009.py',{'host003':'host004','cpu-run002':'cpu-run003','integration006':'integration007'}),
 ('page_review005.py','page_review006.py',{'host003':'host004'}),
 ('page_boundary006.py','page_boundary007.py',{'host003':'host004'}),
 ('linked_review004.py','linked_review005.py',{'host003':'host004'}),
 ('link_review008.py','link_review009.py',{'integration006':'integration007','cpu-run002':'cpu-run003','link-review008':'link-review009'}),
 ('physical006.py','physical007.py',{'review003.json':'review001.json','sources003.json':'sources001.json'})]:
 s=(K/old).read_text()
 for a,b in replacements.items():s=s.replace(a,b)
 fresh(new,s)
s=(K/'source_review.py').read_text().replace('host003','host004').replace('integration006','integration007').replace('source-review001','source-review002')
s=s.replace(",'0x8d8':'0x950'",'')
s=s.replace("'transaction795.c','bridge.S']:","'transaction795.c','bridge002.S']:")
s=s.replace("(O/n.replace('795','793'))","(O/n.replace('795','793').replace('bridge002.S','bridge.S'))")
s=s.replace("if n=='bridge.S':","if n=='bridge002.S':")
s=s.replace(" assert clean(s)==clean((K/n).read_text()),n\nassert 'memory", " if n=='page002.c':s=s.replace('memset(p+0x6400,0,0x8d8)','memset(p+0x6400,0,0x950)')\n assert clean(s)==clean((K/n).read_text()),n\nassert 'memory")
fresh('source_review002.py',s)
print('Preserved first failure; created fresh corrected source versions')
