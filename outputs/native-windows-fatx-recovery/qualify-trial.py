"""Combine independent physical short-trial evidence without claiming long-soak stability."""
import hashlib
import json
import pathlib

k = pathlib.Path(__file__).resolve().parent
read = lambda name: json.loads((k / name).read_text())
sha = lambda data: hashlib.sha256(data).hexdigest()
trial = read('physical-trial.json')
before = read('artifacts/trial/previous-system-events.json')
after = read('trial-system-events.json')
application = read('trial-application-events.json')
assert before['sha256'] == trial['checks']['previous-system.evt']['sha256']
assert after['sha256'] == trial['collected']['system.evt']['sha256']
assert application['sha256'] == trial['collected']['application.evt']['sha256']
assert sha((k/'artifacts/trial/report.txt').read_bytes()) == trial['report']['sha256']
maximum = max(row['record'] for row in before['records'])
new = [row for row in after['records'] if row['record'] > maximum]
delayed = [row for row in new if (row['source'] == 'Ftdisk' and row['event_id'] == 50)
           or any('delayed write failed' in s.lower() for s in row['strings'])]
starts = [row for row in new if row['source'] == 'EventLog' and row['event_id'] == 6005]
stops = [row for row in new if row['source'] == 'EventLog' and row['event_id'] == 6006]
mapped = [line for line in trial['report']['text'].splitlines() if line.startswith('mapped case=')]
allocation = read('physical-trial-allocation.json')
audit = read('posttrial-audit.json')
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
         full_F_allocation_consistent=allocation['allocation_consistent'],
         immutable_binaries_checked=audit['checked'], registry_hives_checked=len(audit['hives']),
         binary_and_hive_audit_passed=audit['complete'] and audit['passed'],
         automatic_test_startup_disabled=not trial['startup_restart_enabled'],
         prior_five_minute_physical_failure_resolved=False,
         next_test='Separate controlled 300-case/five-minute hardware soak; do not claim it has passed.')
r['passed'] = (trial['passed'] and len(mapped)==30 and normal_restart and not delayed
               and r['full_F_allocation_consistent'] and r['binary_and_hive_audit_passed']
               and audit['checked']==audit['expected_count']==3439 and len(audit['hives'])==9
               and all(h['tree']['passed'] and h['matching_sequences'] and h['checksum_valid'] for h in audit['hives'])
               and r['automatic_test_startup_disabled'])
(k/'physical-trial-qualification.json').write_text(json.dumps(r, indent=2)+'\n')
print('Bounded physical trial qualification:', r['passed'], '; delayed writes:', len(delayed),
      '; other error events:', len(r['other_error_records']))
