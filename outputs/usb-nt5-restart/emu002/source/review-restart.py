"""Join cold helper/probe records to restart and integrity evidence."""
import hashlib,importlib.util,json,re,sys
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[1];case=sys.argv[1]
assert re.fullmatch('emu[0-9]{3}',case)
run=repo/('work/runs/nt5xidrestart-'+case);out=k/case
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (run/'cleanup.json').exists()
review=read(k/(case+'-review.json'));details=read(out/'details.json');typed=read(out/'device-state.json')
probe=(run/'probe.log').read_bytes();helper=(run/'wizard201.log').read_bytes()
rows=[]
for line in probe.decode('ascii').splitlines():
    if re.fullmatch('[0-9a-f]{26}',line):continue
    match=re.fullmatch('([A-Z_]+) ([0-9a-f]{8}) tick=([0-9]+)',line)
    assert match,line
    rows.append((match[1],int(match[2],16),int(match[3])))
# The original strict helper analyzer expects decimal guardian records. This
# explicit adaptation uses only original probe values; raw logs are also kept.
guardian='\n'.join(('HELPER_JOIN_RESULT' if n=='HELPER_JOIN' else n)+' '+str(v) for n,v,t in rows)+'\n'
parser=repo/'outputs/setup-wizard-automation201/analyze-cancel002.py'
spec=importlib.util.spec_from_file_location('cancel_review',parser);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
action=module.analyze(helper,guardian.encode('ascii'))
observation=read(run/'observe.json')
optional_exit_only=review['collection_errors']==["exit.txt: 'exit.txt'"]
required_collection_ok=not review['collection_errors'] or optional_exit_only
integrity=(review['protected_exact'] and review['allocation_consistent'] and not review['orphan_cluster_count']
    and not review['allocation_errors'] and required_collection_ok
    and all(all(h[key] for key in ['header_valid','checksum_valid','sequences_equal']) for h in review['hives'].values())
    and all(h['parsed'] for h in details['hives'].values())
    and details['event_history_preserved'] and details['setupapi_history_preserved']
    and typed['selected_policy_unchanged'] and typed['no_new_device_disabling'])
passed=(review['hid_read_pass'] and review['driver_installed'] and action['cancellation_lifecycle_passed'] and integrity
    and review['normal_restart_requested'] and observation['dashboard_returned'] and details['normal_shutdown_count']==1)
result=dict(case=case,physical_access=False,scoped_restart_passed=bool(passed),cold_integrity_passed=bool(integrity),
    collection_errors_retained=review['collection_errors'],shell_exit_marker_optional=optional_exit_only,
    shell_exit_note='Shell exit echo follows probe process exit and is not a required pre-restart record. Its absence is retained; normal shutdown and dashboard return are independently required.',
    helper=action,helper_parser_sha256=sha(parser),probe_sha256=sha(run/'probe.log'),helper_log_sha256=sha(run/'wizard201.log'),
    dashboard_returned=observation['dashboard_returned'],normal_shutdown_count=details['normal_shutdown_count'],
    strict_events_passed=details['strict_events_passed'],device_lifecycle_qualified=False,physical_qualified=False,
    limits='Known wizard cancellation is a diagnostic intervention, not supported hardware installation. No controller stop/removal/power or subsequent-boot qualification.')
(out/'restart-review.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({n:result[n] for n in ['scoped_restart_passed','cold_integrity_passed','dashboard_returned','normal_shutdown_count','strict_events_passed']}))
