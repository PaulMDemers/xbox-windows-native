"""Review the completed emulator replay; never starts or contacts a console."""
import datetime,hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent;ws=k.parents[1]
run=ws/'work/runs/nt5-paint-matched-001'
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=read(k/(run.name+'-save-audit.json'));assert audit['passed']
assert len(audit['files'])==16 and all(f['bytes_match_input'] for f in audit['files'])
assert all(d['matches'] for d in audit['drivers'])
assert audit['runner_log']=='ATTEMPT_ONCE\r\nREPLAY_EXIT_ZERO\r\nNORMAL_RESTART_REQUEST\r\n'
log=[line.split() for line in audit['matched_log'].splitlines()]
assert sum(x[0]=='CASE_PASS' for x in log)==16 and log[-1][:4]==['PASS','16','29','16']
for case in range(16):
    rows=[x for x in log if int(x[1])==case]
    assert sum(x[0]=='WRITE_BEGIN' for x in rows)==(29 if case%2==0 else 0)
    if case%2==0:
        assert [int(x[3]) for x in rows if x[0]=='WRITE_END']==[14,40]+[16384]*27
    assert next(x for x in rows if x[0]=='CASE_PASS')[2:4]==['29','442422']
fixture=read(k/'matched-fixture.json');build=read(k/'matched-build-review.json')
assert fixture['helpers'][0]['sha256']==build['sha256']==sha(k/'artifacts/matched.exe')
assert build['source_sha256']==sha(k/'matched.c')
events=[x for x in read(k/(run.name+'-system-events.json'))['records'] if x['record']>46]
assert events[-1]['event_id']==6006
assert not any(x['event_id']==50 or any('Delayed Write' in s for s in x['strings']) for x in events)
app=read(k/(run.name+'-application-events.json'))
assert app['sha256']==read(k/'nt5-paint-trace-001-application-events.json')['sha256']
assert (run/'cleanup.json').exists() and (run/'dashboard-return.json').exists()
artifacts={p.relative_to(ws).as_posix():sha(p) for p in sorted(run.glob('*.png'))}
for name in ['manifest.json','launch-command.json','dashboard-return.json','cleanup.json']:
    p=run/name
    if p.exists():artifacts[p.relative_to(ws).as_posix()]=sha(p)
r=dict(scope=__doc__,reviewed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),run=run.name,
       passed=True,files=16,verbose_cases=8,quiet_cases=8,writes_per_file=29,bytes_per_file=442422,
       helper_sha256=build['sha256'],source_sha256=build['source_sha256'],
       normal_restart=True,new_system_records=events,application_unchanged=True,
       emulator_closed=True,driver_changes=False,physical_access=False,artifacts=artifacts,
       limitations=['Physical Paint Save freeze remains unresolved.',
                    'No debugger, added pressure, or I/O throttle in this matched replay.',
                    'Cold saved-file and driver checks, not a full volume allocation or hive audit.',
                    'HID7000/Ftdisk49 and two shutdown rundll32 popups remain.',
                    'Replays observed file API sequence, not Paint heap layout or concurrent GUI behavior.'])
(k/'matched-emulator-validation.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS: 16 complete cold BMPs, 8 quiet cases, normal restart; physical freeze unresolved.')
