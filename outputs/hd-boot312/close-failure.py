"""Failure-aware closeout; never alter frozen gates or recollect guest files."""
import datetime,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'final-review.json';assert not dest.exists()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
pins={}
for name in ['emulator-frozen.json','host-frozen.json']:
 data=read(k/name)
 for n,h in data.items():
  p=Path(n);p=p if p.is_absolute() else ws/p;assert sha(p)==h,n
 pins[name]=len(data)
fixtures=[read(k/c/'fixture.json') for c in ['control001','candidate001']]
assert fixtures[0]['parent_sha256']==fixtures[1]['parent_sha256']
changed=[n for n in fixtures[0]['files'] if fixtures[0]['files'][n]!=fixtures[1]['files'][n]]
assert changed==['E/Applications/XWNFBoot/default.xbe']
rows={}
for case in ['control001','candidate001']:
 out=k/case;run=Path('D:/xwn312/runs')/('nt5-hd312-'+case)
 a=read(out/'audit.json');closure=read(out/'closure.json');host=read(run/'host-exit.json');allocation=read(out/'allocation.json')
 assert closure['closed'] and closure['never_relaunch_or_recollect']
 assert closure['audit_sha256']==sha(out/'audit.json') and closure['cleanup_sha256']==sha(run/'cleanup.json')
 assert host['passed'] and host['exit_code']==0 and not host['fallback_kill']
 assert sha(Path(read(out/'fixture.json')['fixture_path_windows']))==read(out/'fixture.json')['fixture_sha256']
 artifacts={p.relative_to(out).as_posix():sha(p) for p in sorted((out/'artifacts').rglob('*')) if p.is_file()}
 (out/'private-artifacts.json').write_text(json.dumps(artifacts,indent=2)+'\n')
 records={n:dict(sha256=sha(run/n),record=read(run/n)) for n in ['cleanup.json','host-exit.json','host-close.json','input-hashes.json']}
 (out/'host-records.json').write_text(json.dumps(records,indent=2)+'\n')
 rows[case]=dict(scoped_passed=a['scoped_combined_passed'],strict_passed=a['strict_qualification_passed'],normal_shutdown_count=a['normal_shutdown_count'],dashboard_return=a['dashboard_return'],integrity_passed=a['integrity_passed'],warnings_errors=a['warnings_errors'],actual_caps=a['actual_caps'],protected_files=len(a['files']),hives=len(a['hives']),allocation={n:allocation[n] for n in ['directories','files','directory_clusters','errors','orphan_cluster_count']},orderly_host_exit=True,private_files=len(artifacts))
assert rows['control001']['scoped_passed'] and not rows['candidate001']['scoped_passed']
out=k/'candidate001';lines=(out/'artifacts/attempt.log').read_text().splitlines();wizard=(out/'artifacts/wizard201.log').read_text().splitlines()
assert lines[-2:]==['WIZARD_EXIT 15','MEASUREMENT_BLOCKED_WIZARD_FAILURE']
assert not any(v.startswith('MEASUREMENT_BEGIN') for v in lines)
assert wizard[-1].startswith('TIMEOUT201 1 0 ') and not any(v.startswith('CANCEL_SENT ') for v in wizard)
assert not (out/'combined-review.json').exists()
failure=dict(checker_sha256=sha(k/'review-combined.py'),error='AssertionError: len(checkpoints)==2 and len(ends)==1',scope='Original checker correctly refuses absent measurement interval; no replacement PASS',checkpoints=sum(v.startswith('CHECKPOINT_TIME ') for v in lines),ends=sum(v.startswith('MEASUREMENT_END_TIME ') for v in lines))
(out/'combined-review-failure001.json').write_text(json.dumps(failure,indent=2)+'\n')
observed=read(out/'register-observation.json');values={}
for a,reply in observed['queries'].items():
 hits=re.findall(r'^0*'+a[2:]+r':\s+0x([0-9a-f]{8})\s*$',reply,re.M);assert len(hits)==1;values[a]=int(hits[0],16)
assert values=={'0xfd600800':0x3700000,'0xfd680838':1279,'0xfd680818':719,'0xfd680600':0x100030}
run=Path('D:/xwn312/runs/nt5-hd312-candidate001');frame=read(run/'timeout-frame001.json')
assert frame['address']=='0x3700000' and (frame['width'],frame['height'],frame['pitch'])==(1280,720,5120)
diag={n:sha(run/n) for n in ['timeout-frame001.png','timeout-frame001.json']}
(out/'diagnostic-captures.json').write_text(json.dumps(dict(files=diag,framebuffer_capture_paused_and_resumed=True,additional_hmp_screendump='Unknown command; no capture or guest mutation',loader_observation='Kernel-range EIP/HLT; old loader code not resident and state overwritten, so no interpretation of its stale fields',scope='Observed720p Windows desktop and four registers, no drawing/workload/normal-shutdown proof'),indent=2)+'\n')
original=read(k/'harness-provenance.json');deltas=[n for n,v in original.items() if sha(k/n)!=v['new_sha256']]
assert deltas==['freeze.py']
r=dict(reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scoped_passed=False,strict_passed=False,physical_access=False,release_qualified=False,rows=rows,pins=pins,changed_files=changed,candidate_failure='Known eligible wizard never satisfied active/foreground predicate; zero actions,120090ms helper timeout, supervisor blocked measurement. No normal shutdown. Exact failing subpredicate was not logged.',observed_registers=values,diagnostic_captures=diag,prelaunch_harness_delta='freeze.py expanded311 source pin closure after initial derivation; final bytes frozen before launch',all_owned_sessions_closed=True,limits='720p desktop observation only; not qualified Windows720p or1080i. Clean allocation/hive/protected checks do not prove full file-content safety after interrupted run. Never relaunch/recollect/parent either runtime.')
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({n:r[n] for n in ['scoped_passed','strict_passed','pins','candidate_failure','all_owned_sessions_closed']},indent=2))
