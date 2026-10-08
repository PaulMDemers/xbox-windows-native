"""Reconcile three unique closed attempts, unchanged guest inputs and explicit failures."""
import hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];read=lambda p:json.loads(p.read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
host=lambda p:Path(p.replace('/mnt/c/','C:/').replace('/mnt/e/','E:/'))
rows=[];identities=set();guest=None
for name in ['video-ram-crash','video-ram-crash2','video-ram-crash3']:
 kit=k.parent/name;out=kit/'crash001';run=ws/'work/runs'/('nt5-'+name+'-crash001')
 assert str(run) not in identities;identities.add(str(run))
 f=read(kit/'fixture-crash001.json');pre=read(out/'preflight.json');c=read(out/'closure.json');a=read(out/'audit.json');t=read(out/'trace.json')
 assert (run/'cleanup.json').exists() and c['never_relaunch']
 assert sha(run/'hdd.qcow2')==c['private_disk_sha256']==a['crash_disk_sha256']
 for n,h in c['metadata_sha256'].items():assert sha(run/n)==h
 for n,h in pre['sources'].items():assert sha(out/'source'/n)==h
 assert sha(ws/'outputs/native-windows-fatx-forensics/artifacts'/f['fixture_name'])==f['fixture_sha256']
 signature=dict(parent=f['parent_manifest_sha256'],protected=f['protected'],payloads=f['payloads'],startup=f['startup_sha256'],build=f['build_review_sha256'])
 if guest is None:guest=signature
 else:assert signature==guest
 if name!='video-ram-crash3':
  failed=read(kit/'failure-verification.json');assert failed['failure_preserved'] and not failed['passed']
 else:assert read(kit/'ram-verification.json')['strict_diagnostic_passed']
 assert t['guest_resumed'] and not t['armed_breakpoints_remaining']
 rows.append(dict(kit=name,run=str(run),trace_status=t['status'],allocation_passed=a['allocation_passed'],dump_write_evidence_passed=a['dump_write_evidence_passed'],closure_sha256=sha(out/'closure.json')))
for parent in read(k/'fixture-crash001.json')['parents']:assert sha(host(parent['path']))==parent['sha256']
r=dict(passed=True,physical_access=False,unique_closed_attempts=3,unchanged_guest_helpers_drivers_parent=True,all_frozen_sources_exact=True,
 all_breakpoints_removed_and_guests_resumed=True,parents_unchanged=True,attempts=rows,
 limits='Only third explicit mapped-page protocol qualifies. Failed first two attempts retained; no whole RAM-code residency, physical or new recovery qualification.')
dest=k/'history-review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
