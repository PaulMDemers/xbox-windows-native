"""Resume ONLY recorded unlaunched206 control after missing local probe filename.
No second launch, directory creation, recapture, or replacement of earlier evidence.
"""
import hashlib,importlib.util,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case='control001';out=k/case
sys.argv=['physical-controller.py','inspect',case]
spec=importlib.util.spec_from_file_location('resume_controller',k/'physical-controller.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
dest=out/'prelaunch-resume.json';assert not dest.exists()
r=c.read(c.record);assert not r['launch_requested'] and not r['startup_enabled'] and not r['baseline_restored']
assert r['rollback_entries']==32 and r['before_payloads'][c.xwnown] is None
replay=k/'artifacts/replay.exe';alias=k/'artifacts/gdi-probe.exe';assert not alias.exists()
data=replay.read_bytes();assert c.sha(data)==c.package['helpers']['replay.exe']
alias.write_bytes(data);assert alias.read_bytes()==data
c.ready()
review=dict(prelaunch_failure='Missing local artifacts/gdi-probe.exe path, after runner and rollback staging, BEFORE driver/SYSTEM/startup writes or SITE EXEC.',
 physical_boot_attempted=False,source_sha256=c.sha(Path(__file__).read_bytes()),controller_sha256=c.sha((k/'physical-controller.py').read_bytes()),
 ready_sha256=c.sha((k/'physical-ready.json').read_bytes()),alias_sha256=c.sha(data),alias_matches_pinned_replay=True,
 original_record_sha256=c.sha(c.record.read_bytes()),status='verifying_original_state')
def save():dest.write_text(json.dumps(review,indent=2)+'\n',encoding='utf-8')
save()
with c.m.connect() as f:
 c.m.owner(f);checks=c.fixed_checks(f)
 assert c.m.get(f,c.startup)==(c.art/'before-startup.cmd').read_bytes()
 assert c.sha(c.m.get(f,'/F/'+c.rollback_dir+'/current-rollback206.zip'))==r['rollback_sha256']
 assert c.sha(c.m.get(f,'/F/'+c.namespace+'/runner.exe'))==c.package['helpers']['runner.exe']
 for name in ['replay.exe','wizard.exe','attempt.log','sample0']:
  assert c.absence(f,'/F/'+c.namespace,name),name
 review.update(original_startup_and_baseline_exact=True,known_partial_helpers_verified=True,status='staging_missing_helpers');save()
 c.m.put(f,'/F/'+c.namespace+'/replay.exe',data)
 c.m.put(f,'/F/'+c.namespace+'/wizard.exe',(k/'artifacts/wizard.exe').read_bytes())
 try:
  for path,p,expected in c.changes:
   blob=p.read_bytes();assert c.sha(blob)==expected;c.m.put(f,path,blob)
  c.m.put(f,c.system,c.proposal.read_bytes())
  c.m.put(f,c.startup,c.test_startup);r['startup_enabled']=True;c.save(r)
 except Exception as exc:
  r['prelaunch_failure']=repr(exc);c.save(r);c.restore(f,r);review.update(status='staging_failed_restored',error=repr(exc));save();raise
 # Persist actual launch intent BEFORE requesting the single launch.
 r.update(launch_requested=True,launch_utc=c.m.utc(),command=r'SITE EXEC E:\Applications\XWNFBoot\default.xbe',resumed_prelaunch=True)
 c.save(r);review.update(status='single_launch_requested',launch_utc=r['launch_utc']);save()
 try:r['reply']=f.sendcmd(r['command'])
 except Exception as exc:r['reply_uncertain']=type(exc).__name__
 c.save(r);review.update(status='launch_recorded',reply_uncertain=r.get('reply_uncertain'),reply=r.get('reply'));save()
print('Unlaunched206 control safely resumed; SINGLE launch recorded, never repeat')
