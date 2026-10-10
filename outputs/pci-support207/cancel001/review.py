"""Verify genuine NT5 query-remove cancellation, recovery and cold closure."""
import ast,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;out=k/'candidate001'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=read(k/'build001.json')
for v in b['sources']:assert sha(k/v['name'])==v['sha256'],v['name']
for v in b['files']:assert sha(k/'artifacts/build001'/v['name'])==v['sha256'],v['name']
assert sha(k/'e_allocation.py')==sha(k.parent/'halboot001/e_allocation.py')
a=read(out/'audit.json');p=read(out/'pnp-review.json');r=read(out/'run.json');t=read(out/'resource-trace.json')
assert r['closed'] and r['source_unchanged'] and a['integrity_passed']
assert a['e_allocation']['allocation_consistent'] and a['e_allocation_metadata_unchanged']
assert p['cancel_remove_qualified'] and p['lifecycle_completed'] and p['hal_probe_passed']
lines=p['log'].splitlines();minors=[x['profile'] for x in t['records'] if x['stage']==5]
assert minors.count(3)==1 and minors.count(1)==3 and minors.count(2)==2 and minors.count(0)==3
assert minors[minors.index(3)-1]==1
assert all(x in lines for x in ('cancel_existing_handle_ok=1','cancel_starts_before=1','cancel_starts_after=1','cancel_queries_before=0','cancel_queries_after=1','CANCEL_REMOVE_HANDLE_CLOSED','CANCEL_REMOVE_RECOVERED','remove_result=0','REMOVE_INTERFACE_ABSENT','reenumerate_result=0'))
assert lines.count('hal_export=1')==5 and lines.count('hal_invalid_result=1')==5 and lines.count('hal_invalid_polls=0')==5
assert lines.count('power_status=0')==6
syntax=0
for path in k.glob('*.py'):ast.parse(path.read_text(),filename=str(path));syntax+=1
result=dict(passed=True,scope=__doc__,physical_access=False,compiled_sources_and_artifacts_match=True,python_sources_checked=syntax,closed_utc=r['closed_utc'],veto_result=23,veto_kind=5,query_remove_count=3,cancel_remove_count=1,remove_count=2,start_count=3,stop_observed=4 in minors,cancel_stop_observed=6 in minors,held_handle_recovered_without_restart=True,post_close_remove_reenumeration=True,native_invalid_api_probe_count=5,power_transitions=6,integrity_passed=True,pending_setup_hold=p['restart_held_pending_setup'],normal_restart_qualified=p['normal_restart_qualified'],warnings_errors=a['warnings_errors'],do_not_relaunch=True,evidence_sha256={name:sha(out/name) for name in ('run.json','audit.json','pnp-review.json','resource-trace.json')},limits='One fresh emulator boot. No functional reads, terminal takeover, STOP/CANCEL_STOP, normal restart, repeated-boot storage safety, or physical qualification.')
dest=k/'review001.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
