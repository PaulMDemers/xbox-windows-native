"""Combine the bounded physical replay and independent post-reboot checks."""
import json,pathlib,datetime
k=pathlib.Path(__file__).resolve().parent;r=k.parent/'native-windows-fatx-recovery'
load=lambda p:json.loads(p.read_text())
trial=load(k/'physical-replay.json');assert trial.get('collected_utc') and not trial['startup_restart_enabled']
before=load(k/'physical-before-system-events.json');after=load(k/'physical-after-system-events.json')
last=max((v['record'] for v in before['records']),default=0)
events=[v for v in after['records'] if v['record']>last]
delayed=[v for v in events if any('delayed write' in s.lower() for s in v['strings']) or
         (v['event_id']==50 and v['source'].lower() in ('ftdisk','disk'))]
allocation=load(k/'physical-replay-allocation.json');audit=load(r/'postreplay-audit.json')
scan=load(r/'physical-postreplay.json')
checks=dict(workload_passed=trial['workload_passed'],normal_eventlog_stop=any(v['event_id']==6006 and v['source']=='EventLog' for v in events),
 no_new_delayed_write_events=not delayed,allocation=allocation['allocation_consistent'],
 no_orphans=allocation['orphan_cluster_count']==0,binaries_and_hives=audit['complete'] and audit['passed'] and audit['checked']==3439 and len(audit['hives'])==9,
 scanner_completed=scan['completed'],user_partial_preserved=trial['user_partial_unchanged'],startup_disabled=not trial['startup_restart_enabled'])
old_app=load(k/'physical-before-application-events.json');new_app=load(k/'physical-after-application-events.json')
last_app=max((v['record'] for v in old_app['records']),default=0)
result=dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,passed=all(checks.values()),
 system_records=events,application_records=[v for v in new_app['records'] if v['record']>last_app],
 interpretation='Bounded synthetic writes on hardware; does not resolve the original Paint save hang or prove general driver stability.')
(k/'physical-replay-qualification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
trial.pop('qualification_pending',None)
trial.update(qualification_report='physical-replay-qualification.json',bounded_qualification_passed=result['passed'])
(k/'physical-replay.json').write_text(json.dumps(trial,indent=2)+'\n')
assert result['passed']
