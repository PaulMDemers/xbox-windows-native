"""Accept only the completed scoped physical398 result; one E driver write, no boot."""
import sys,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(K.parent/'setup-candidate398'))
from physical import connect,fetch,store,pins,sha,utc,write_json,FATX,START,CANDIDATE
case='candidate001';T=K.parent/'setup-candidate398'/case
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
from gates import validation
a=validation();f=read(T/'final-state.json');c=read(T/'collection.json')
assert f['closed'] and f['normal_startup_restored'] and f['original_driver_restored']
assert all(a[n] for n in ['diagnostic_workload_completed','scoped_combined_passed','cmd_persistence_passed','file_persistence_passed','tested_fatx_verified','integrity_passed','mode720p_passed'])
assert a['normal_shutdown_count']==1 and c['completed'] and c['driver_restored']
# Strict warning result is carried unchanged; this accepts only scoped demo use.
original=(K.parent/'setup-candidate398/artifacts/candidate001-before'/FATX.lstrip('/')).read_bytes()
candidate=(K.parent/'setup-candidate398/artifacts/candidate001/tested-fatx.sys').read_bytes()
assert sha(candidate)==CANDIDATE and sha(original)==f['files'][FATX]['sha256'];pins()
dest=K/'accepted-state.json';assert not dest.exists()
pkg=read(K.parent/'demo-settings376/package001.json')
for name,row in pkg['files'].items(): f['files']['/E/xwndemo372/'+name]=row
r=dict(accepted=False,write_requested=False,physical_writes=[FATX],console_C_accessed=False,driver_only=True,original_sha256=sha(original),candidate_sha256=sha(candidate),physical_trial='setup-candidate398/candidate001',audit_sha256=sha((T/'corrected-analysis002.json').read_bytes()),original_audit_preserved=True,strict_qualification_passed=a['strict_qualification_passed'],warnings_errors=a['warnings_errors'],public_release=False,created_utc=utc());write_json(dest,r)
with connect() as ftp:
 for p,v in f['files'].items():assert sha(fetch(ftp,p))==v['sha256'],p
 r['write_requested']=True;write_json(dest,r)
 try:
  store(ftp,FATX,candidate,case)
  r['verified_files']={}
  for p,v in f['files'].items():
   expected=CANDIDATE if p==FATX else v['sha256'];actual=sha(fetch(ftp,p));assert actual==expected,p;r['verified_files'][p]=actual
 except BaseException as e:
  r['error']=repr(e);write_json(dest,r)
  try:
   store(ftp,FATX,original,case);r['original_restored_after_failure']=True
  except BaseException as rollback_error:
   r['original_restored_after_failure']=False;r['rollback_error']=repr(rollback_error)
   write_json(dest,r);raise
  write_json(dest,r);raise
 r.update(accepted=True,normal_startup_retained=True,video_audio_720p_and_F_rollback_unchanged=True,launch_requested=False,completed_utc=utc());write_json(dest,r)
print('Scoped physical FATX390 accepted/readback; no boot; normal720p startup retained')
