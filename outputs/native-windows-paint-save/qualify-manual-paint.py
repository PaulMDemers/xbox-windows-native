"""Qualify two user-reported Paint saves with independent post-reboot evidence."""
import datetime,hashlib,importlib,json,pathlib
m=importlib.import_module('manual-paint');k=m.k;recovery=k.parent/'native-windows-fatx-recovery'
load=lambda p:json.loads(p.read_text())
trial=load(m.record);assert trial.get('collected_utc')
before=load(k/'paint-repeat-before-system-events.json');after=load(k/'paint-repeat-after-system-events.json')
last=max(e['record'] for e in before['records']);events=[e for e in after['records'] if e['record']>last]
delayed=[e for e in events if any('delayed write' in s.lower() for s in e['strings']) or (e['source'].lower() in ('ftdisk','disk') and e['event_id']==50)]
files=trial['discovered_desktop_bitmaps'];file_checks={}
for name,row in files.items():
 data=(m.m.folder/('after-'+name)).read_bytes()
 file_checks[name]=hashlib.sha256(data).hexdigest()==row['sha256'] and m.bitmap(data)['complete_24bit_bmp'] and row['independent_decoder_passed']
allocation=load(k/'physical-paint-repeat-allocation.json');audit=load(recovery/'postpaintrepeat-audit.json');scan=load(recovery/'physical-postpaintrepeat.json')
checks=dict(user_reported_two_saves_and_reopens=trial['user_reported_save_count']==2 and trial['user_reported_reopen_success'],
 two_complete_cold_bitmaps=len(files)==2 and all(file_checks.values()),drivers_unchanged=all(trial['driver_checks'].values()),
 original_partial_preserved=trial['user_partial_unchanged'],no_new_delayed_write_events=not delayed,
 normal_eventlog_stop=any(e['source']=='EventLog' and e['event_id']==6006 for e in events),
 allocation=allocation['allocation_consistent'] and allocation['orphan_cluster_count']==0,scanner_completed=scan['completed'],
 binaries_and_hives=audit['complete'] and audit['passed'] and audit['checked']==3439 and len(audit['hives'])==9,
 automatic_startup_disabled=not trial['startup_restart_enabled'] and not trial['startup_paint_enabled'])
oldapp=load(k/'paint-repeat-before-application-events.json');newapp=load(k/'paint-repeat-after-application-events.json')
result=dict(scope=__doc__,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=all(checks.values()),checks=checks,
 user_observation=trial['manual_observation'],files=files,system_records=events,
 application_records=[e for e in newapp['records'] if e['record']>max(v['record'] for v in oldapp['records'])],
 limitations=['Two manual saves/reopens were reported, not the three initially suggested.',
 'The file names differ from the suggestions; discovered desktop files were collected separately and both decoded successfully.',
 'Visual reopening success is user-reported; offline checks validate persisted BMP structure and data availability.',
 'Ftdisk49 and Srv2013 warnings are present; this is not an error-free-system claim.',
 'The single earlier Paint freeze was not reproduced; its cause remains unknown.'])
(k/'physical-paint-repeat-qualification.json').write_text(json.dumps(result,indent=2)+'\n')
trial.pop('qualification_pending',None);trial.update(qualification_report='physical-paint-repeat-qualification.json',bounded_qualification_passed=result['passed'])
m.record.write_text(json.dumps(trial,indent=2)+'\n')
print(json.dumps({'passed':result['passed'],'checks':checks},indent=2));assert result['passed']
