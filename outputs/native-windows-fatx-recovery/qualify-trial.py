"""Combine independent physical trial evidence without claiming general stability."""
import argparse
import hashlib
import json
import pathlib

k = pathlib.Path(__file__).resolve().parent
read = lambda name: json.loads((k / name).read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--kind',choices=['short','soak','long'],default='short');a=p.parse_args()
tag={'short':'trial','soak':'soak','long':'long'}[a.kind]
trial = read('physical-'+tag+'.json')
before = read('artifacts/'+tag+'/previous-system-events.json')
after = read(tag+'-system-events.json')
application = read(tag+'-application-events.json')
assert before['sha256'] == trial['checks']['previous-system.evt']['sha256']
assert after['sha256'] == trial['collected']['system.evt']['sha256']
assert application['sha256'] == trial['collected']['application.evt']['sha256']
assert sha((k/'artifacts'/tag/'report.txt').read_bytes()) == trial['report']['sha256']
maximum = max(row['record'] for row in before['records'])
new = [row for row in after['records'] if row['record'] > maximum]
delayed = [row for row in new if (row['source'] == 'Ftdisk' and row['event_id'] == 50)
           or any('delayed write failed' in s.lower() for s in row['strings'])]
starts = [row for row in new if row['source'] == 'EventLog' and row['event_id'] == 6005]
stops = [row for row in new if row['source'] == 'EventLog' and row['event_id'] == 6006]
mapped = [line for line in trial['report']['text'].splitlines() if line.startswith('map=' if a.kind in ('soak','long') else 'mapped case=')]
allocation = read('physical-'+tag+'-allocation.json')
audit = read('post'+tag+'-audit.json')
normal_restart = len(starts) == len(stops) == 1 and starts[0]['record'] < stops[0]['record']
current_application = [row for row in application['records']
                       if new and row['generated_unix'] >= min(e['generated_unix'] for e in new)]
r = dict(scope=__doc__, filesystem_sha256=trial['expected_drivers']['/F/winnt/system32/drivers/xwnfatx.sys'],
         helper_report_passed=trial['probe_passed'], mapped_cases=len(mapped),
         payloads_verified=all(row['pattern_match'] for row in trial['payloads']),
         driver_hashes_unchanged=all(row['passed'] for row in trial['driver_checks']),
         normal_restart_observed=normal_restart, new_system_records=new,
         application_records_in_trial_time_window=current_application,
         delayed_write_events=len(delayed), other_error_records=[row for row in new if row['type']==1],
         other_warning_records=[row for row in new if row['type']==2 and row not in delayed],
         full_F_allocation_consistent=allocation['allocation_consistent'],
         immutable_binaries_checked=audit['checked'], registry_hives_checked=len(audit['hives']),
         binary_and_hive_audit_passed=audit['complete'] and audit['passed'],
         automatic_test_startup_disabled=not trial['startup_restart_enabled'],
         prior_five_minute_physical_failure_resolved=False,
         next_test='Separate controlled 300-case/five-minute hardware soak; do not claim it has passed.')
r['kind']=a.kind
r['soak_completed']=trial.get('soak_completed',False)
r['archived_previous_payloads_verified']=bool(trial.get('archive_checks')) and all(x['passed'] for x in trial.get('archive_checks',[]))
if a.kind in ('soak','long'):r['next_test']='Repeat-boot persistence and broader workload validation; a bounded pass is not general stability.'
if a.kind=='long':
    observations=k/'manual-long-observations.json'
    r['manual_application_observations']=json.loads(observations.read_text()) if observations.exists() else {'status':'not_yet_reported'}
    r['qualification_scope']='Automated storage workload and integrity checks; manual application results are separate.'
    r['next_test']='Review user application observations, then broader desktop and display-driver tests; long-term storage stability remains unproven.'
    if observations.exists():
        r['next_test']='Verify the two manually saved files after another boot, then broader desktop and display-driver tests; long-term storage stability remains unproven.'
r['passed'] = (trial['passed'] and len(mapped)==(300 if a.kind in ('soak','long') else 30) and normal_restart and not delayed
               and (a.kind=='short' or r['soak_completed'])
               and (a.kind=='short' or r['archived_previous_payloads_verified'])
               and r['full_F_allocation_consistent'] and r['binary_and_hive_audit_passed']
               and audit['checked']==audit['expected_count']==3439 and len(audit['hives'])==9
               and all(h['tree']['passed'] and h['matching_sequences'] and h['checksum_valid'] for h in audit['hives'])
               and r['automatic_test_startup_disabled'])
r['prior_failure_not_reproduced_in_this_soak'] = a.kind in ('soak','long') and r['passed']
(k/('physical-'+tag+'-qualification.json')).write_text(json.dumps(r, indent=2)+'\n')
print('Bounded physical trial qualification:', r['passed'], '; delayed writes:', len(delayed),
      '; other error events:', len(r['other_error_records']))
