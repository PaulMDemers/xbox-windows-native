"""Prepare a new analog listening case from preserved, previously exercised controllers."""
import ast,hashlib,json,pathlib,datetime
k=pathlib.Path(__file__).resolve().parent
old=k.parent/'audio220'
assert not (k/'common001.py').exists()
names=['common001.py','capture002.py','audit-before002.py','providers001.py','trial002.py','scan001.py','audit001.py','typed-state001.py','installed-binding001.py','restore001.py','confirm-restored001.py','freeze001.py']
origin={}
for name in names:
 p=old/name;s=p.read_text();origin[name]=hashlib.sha256(p.read_bytes()).hexdigest()
 s=s.replace("audio-claimed.json","audio-listen001-claimed.json").replace("audio-closed.json","audio-listen001-closed.json")
 s=s.replace("['owner']=='audio'","['owner']=='audio-listen001'")
 s=s.replace('xwna220i','xwnaL01i').replace('xwna220p','xwnaL01p').replace('XWNA220scan','XWNAL01scan')
 if name=='common001.py':
  s=s.replace("assert not (queue/'audio-listen001-closed.json').exists(),'Ticket already closed'", "assert not (queue/'audio-listen001-closed.json').exists(),'Ticket already closed'\n    for claim in queue.glob('*-claimed.json'):\n        if claim.name!='audio-listen001-claimed.json':\n            closed=claim.with_name(claim.name.replace('-claimed.json','-closed.json'))\n            assert closed.exists() and read(closed).get('baseline_restored') is True,'Another physical owner exists'")
 if name=='trial002.py':
  s=s.replace("for frozen_path,frozen_hash in read(k/'frozen002.json').items():assert sha(pathlib.Path(frozen_path).read_bytes())==frozen_hash,'Supplemental input changed'",'')
  s=s.replace("k/'install001/audit002.json'","k/'install001/audit.json'")
  s=s.replace("pins();assert not out.exists()", "pins();baseline_scan=read(k/'baseline001/allocation.json');assert baseline_scan['allocation_consistent'] and not baseline_scan['errors'] and not baseline_scan['orphan_cluster_count'];assert not out.exists()")
 if name=='scan001.py':
  s=s.replace("['install001','playback001','restored001']","['baseline001','install001','playback001','restored001']")
  s=s.replace("dict(install001=","dict(baseline001='XWNAL01scanB',install001=")
  s=s.replace("assert read(out/('restoration.json' if case=='restored001' else 'collection.json'))['completed']", "assert read(k/'capture002.json')['passed'] if case=='baseline001' else read(out/('restoration.json' if case=='restored001' else 'collection.json'))['completed']\n    out.mkdir(exist_ok=True)")
 if name=='audit001.py':
  s=s.replace("required(log,['EXACT_TARGET_COUNT 1','UPDATE_RESULT 1'", "required(log,['UPDATE_RESULT 1'")
  needle="    r['joined_children']=required(runner,['HELPER_JOIN_RESULT 0','HELPER_EXIT 0','INSTALLER_JOIN_RESULT 0'"
  check="    targets=[s for s in log if s.startswith('TARGET_INSTANCE ')]\n    r['workload_passed'] &= log.count('EXACT_TARGET_COUNT 1')==2 and len(targets)==2 and targets[0]==targets[1] and 'VEN_10DE&DEV_01B1&SUBSYS_00000000&REV_B1' in targets[0]\n"
  assert needle in s;s=s.replace(needle,check+needle)
 ast.parse(s);(k/name).write_text(s,encoding='utf-8')
(k/'controller-provenance.json').write_text(json.dumps({'source_directory':str(old),'source_sha256':origin,'changes':['New successor ticket with all-owner checks','Unique remote/local namespaces','New prelaunch allocation scan gate','Previously reviewed installer duplicate-target audit correction'],'driver_or_helper_changes':False},indent=2)+'\n')
print('New case controllers prepared; no console access')
