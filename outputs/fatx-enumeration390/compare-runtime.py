"""Independent comparison of closed original389 and corrected392 evidence."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;W=K.parents[1]
A=K.parent/'file-enumeration389/control001';B=K.parent/'file-enumeration392/candidate001'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def enums(data,expected):
 rows=data.decode('ascii').splitlines()
 for name in ['saved.tmp','saved.bmp']:
  found=[s.split() for s in rows if s.startswith('ENUM_NAME '+name+' ')]
  assert len(found)==expected
  assert found==[['ENUM_NAME',name,str(i),name] for i in range(1,expected+1)]
  assert rows.count('ENUM_END '+name+' '+str(expected)+' '+('18' if expected==1 else '111'))==1
 assert rows.count('ENUM_EXACT 1 18')==(2 if expected==1 else 0)
 assert rows[-1]=='FILE_API_END '+('0' if expected==1 else '2')
 return True
ra,rb=[read(p/'audit.json') for p in [A,B]]
assert enums((A/'artifacts/file-api.log').read_bytes(),32)
assert enums((B/'artifacts/file-api.log').read_bytes(),1)
for r in [ra,rb]:
 assert r['file_bytes_passed'] and r['integrity_passed'] and r['display_workload_passed'] and r['audio_capture']['passed'] and r['normal_shutdown_count']==1 and r['orderly_host_exit']
 assert [(e['source'],e['event_id']) for e in r['warnings_errors']]==[('Ftdisk',49)] and not r['strict_qualification_passed']
assert not ra['file_persistence_passed'] and rb['file_persistence_passed'] and rb['scoped_combined_passed']
fa,fb=[read(p/'fixture.json') for p in [A,B]]
# Compare all shared non-test protected payloads. Namespace/startup differ by ID.
skip={'e/documents and settings/all users/start menu/programs/startup/xwnsetup.cmd'}
x={p:h for p,h in fa['protected'].items() if not p.lower().startswith('e/'+fa['namespace'].lower()+'/') and p.lower() not in skip}
y={p:h for p,h in fb['protected'].items() if not p.lower().startswith('e/'+fb['namespace'].lower()+'/') and p.lower() not in skip}
assert x.keys()==y.keys();changes=[p for p in x if x[p]!=y[p]]
assert changes==['E/winnt/system32/drivers/xwnfatx.sys'],changes
xa={p.split('/',2)[2]:h for p,h in fa['protected'].items() if p.startswith('E/'+fa['namespace']+'/')};xb={p.split('/',2)[2]:h for p,h in fb['protected'].items() if p.startswith('E/'+fb['namespace']+'/')};assert xa==xb
for n in ['system','software','default','sam','security']:assert sha(A/'artifacts'/('before-'+n))==sha(B/'artifacts'/('before-'+n))
negative=0;good=(B/'artifacts/file-api.log').read_bytes()
for old,new in [(b'ENUM_NAME saved.tmp 1 saved.tmp',b'ENUM_NAME saved.tmp 2 saved.tmp'),(b'ENUM_NAME saved.tmp 1 saved.tmp',b'ENUM_NAME saved.tmp 1 wrong.tmp'),(b'ENUM_END saved.bmp 1 18',b'ENUM_END saved.bmp 2 18'),(b'ENUM_END saved.tmp 1 18',b'ENUM_END saved.tmp 1 111'),(b'FILE_API_END 0',b'FILE_API_END 1'),(b'ENUM_EXACT 1 18',b'ENUM_EXACT 0 18')]:
 assert old in good
 try:enums(good.replace(old,new,1),1)
 except AssertionError:negative+=1
 else:raise AssertionError('Mutation accepted')
r=dict(passed=True,closed_cases=['389control001','392candidate001'],only_changed_shared_payload=changes,identical_workload_files=len(xa),unchanged_before_hives=5,original_matches_per_exact_query=32,candidate_matches_per_exact_query=1,independent_negative_cases=negative,physical_qualified=False,cmd_move_not_yet_measured=True,strict_events_passed=False,audit_hashes=[sha(p/'audit.json') for p in [A,B]])
dest=K/'pair-review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
