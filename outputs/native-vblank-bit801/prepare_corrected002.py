"""Create distinct qualification scripts after rejected CPU-mask lineage; no launch."""
from pathlib import Path
import hashlib,json,re
K=Path(__file__).resolve().parent
changes={
 'equivalence002.py':('equivalence001.py',{'model001':'model003','model002':'model004','compact001':'compact002','equivalence001':'equivalence002'}),
 'payload_build008.py':('payload_build007.py',{'payload007':'payload008','probe-compact.c':'probe-compact-native.c'}),
 'plan_test003.py':('plan_test002.py',{'host-plan004':'host-plan005'}),
 'host_build008.py':('host_build007.py',{'host005':'host006','payload007':'payload008','plan_test002':'plan_test003'}),
 'integration011.py':('integration010.py',{'host005':'host006','integration008':'integration009'}),
 'cpu004.py':('cpu003.py',{'host005':'host006','cpu003':'cpu004','cpu-build003':'cpu-build004','cpu-run003':'cpu-run004'}),
 'optical_review004.py':('optical_review003.py',{'host005':'host006'}),
 'build011.py':('build010.py',{'host005':'host006','cpu-run003':'cpu-run004','integration008':'integration009'}),
 'link_review011.py':('link_review010.py',{'payload007':'payload008','link-review010':'link-review011','model001':'model004','integration008':'integration009','cpu-run003':'cpu-run004'}),
 'linked_review006.py':('linked_review005.py',{'host005':'host006'}),
 'page_review007.py':('page_review006.py',{'host005':'host006'}),
 'page_boundary008.py':('page_boundary007.py',{'host005':'host006'}),
}
records={}
for name,(old,mapping) in changes.items():
 p=K/name;assert not p.exists()
 s=(K/old).read_text()
 for a,b in mapping.items():s=s.replace(a,b)
 p.write_bytes(s.encode())
 records[name]={'source':old,'source_sha256':hashlib.sha256((K/old).read_bytes()).hexdigest(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'replacements':mapping}
for name in ['probe-native.c','probe-compact-native.c']:
 s=(K/name).read_text()
 assert '(o->cr0&0xe0000001)!=0x40000001 || o->cr3!=0 || (flags&0x200)' in s
 assert not re.search(r'0x801(?:00001|10031)\b',s)
(K/'corrected-lineage002.json').write_text(json.dumps({'physical_access':False,'scripts':records,'correct_native_CPU_guard':True},indent=2)+'\n')
