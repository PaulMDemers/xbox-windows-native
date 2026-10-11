"""Verify the physical channel case and exact rollback, then close its new ticket."""
import ast,datetime,hashlib,json,pathlib,re
k=pathlib.Path(__file__).resolve().parent;repo=k.parents[1]
state=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-hardware220/state')
delivery=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-09/xbox-windows2000-audio/outputs')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not (state/'audio-channel001-closed.json').exists()
frozen=read(k/'frozen001.json')
for p,h in frozen.items():assert sha(pathlib.Path(p))==h,p
for p in k.glob('*.py'):ast.parse(p.read_text())
a=read(k/'install001/audit.json');b=read(k/'playback001/audit.json')
assert a['scoped_installation_passed'] and b['scoped_runtime_passed']
for r in [a,b]:
 assert r['normal_shutdown_count']==1 and r['dashboard_return'] and r['integrity_passed']
 assert {(v['source'],v['event_id']) for v in r['warnings_errors']}=={('Ftdisk',49)} and not r['strict_qualification_passed']
for c in ['baseline001','install001','playback001','restored001']:
 r=read(k/c/'allocation.json');assert r['allocation_consistent'] and not r['errors'] and not r['orphan_cluster_count']
r=read(k/'restored001/restoration.json');final=read(k/'restored001/confirmation.json')
assert r['completed'] and r['baseline_restored'] and all(r['checks'].values()) and final['passed']
observations=[read(p) for p in sorted(k.glob('user-observation*.json'))]
dedicated=[v for v in observations if v.get('case')=='playback001']
channel_verified=any(v.get('stereo_channel_mapping_verified') is True for v in dedicated)
evidence=['capture002.json','before-audit002.json','providers001.json','frozen001.json','install001/audit.json','playback001/audit.json','restored001/restoration.json','restored001/confirmation.json']
evidence += [p.name for p in sorted(k.glob('user-observation*.json'))]
review={'passed':True,'reviewed_utc':utc(),'frozen_inputs_verified':len(frozen),'physical_runtime_passed':True,'user_observations':observations,'stereo_channel_mapping_verified':channel_verified,'instrumented_physical_capture':False,'strict_whole_boot_passed':False,'strict_failure':'Ftdisk49','baseline_restored':True,'restored_readback_files':len(r['checks']),'evidence_sha256':{n:sha(k/n) for n in evidence}}
(k/'review001.json').write_text(json.dumps(review,indent=2)+'\n')
observation_text='\n'.join('- '+v['user_report'] for v in observations) if observations else 'No user listening observation was received before closure.'
text=f'''# Xbox dedicated channel listening trial

The unchanged build004 ACI driver passed genuine installation and a subsequent
physical playback boot using the new channel-identification helper. All six
three-second phases completed, followed by normal restart and cold integrity
checks. The captured incoming baseline is restored and verified.

## Listening observations

{observation_text}

Correct physical left/right mapping verified by user observation: **{'yes' if channel_verified else 'no'}**.
The earlier audio-listen001 login-sound observation remains valid independently.
Runtime completion alone is not a new listening observation. No instrumented
physical audio capture was made; measured quality remains unqualified.

## Results

| Gate | Result |
| --- | --- |
| Genuine installation | Exact ACI target, SetupAPI success, xwnaci207 binding, problem 0. |
| Subsequent runtime | xwnaci207 module present, legacy module absent; six complete 144,000-frame phases with masks left/right/both repeated twice. |
| Pattern | Each phase has two seconds of low-level tone and one second of encoded silence, followed by a 350 ms inter-cycle pause. Left 400 Hz; right 600 Hz. |
| Shutdown | Joined helpers, unforced restart, one new EventLog6006 and dashboard return on both Windows boots. |
| Cold integrity | Five full hives, protected bytes, preserved event/setup history and policy checks passed. |
| Allocation | Baseline, post-install, post-playback and post-restore scans all passed with zero errors/orphans. |
| Rollback | {len(r['checks'])} readback checks; {len(r['writes'])} changed files restored; {len(r['removed'])} exact new files removed after preservation. |
| Strict qualification | FAIL: Ftdisk49 remains on both Windows boots. |

Known unrelated wizard cancellation prevents prompt-free boot qualification.
APU, digital output, capture, hardware mixer, protected content, suspend/resume,
future video integration and general repeated-boot storage safety remain outside
these results. Separate emulator storage failures are not resolved by this trial.

## Candidate and preparation

Driver version 0.0.4.207, SHA256
`c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
New helper SHA256
`5ddf733be56e5bbffbcf1ad69f69a6fe31584d4635683a37dd18a0b5c912db77`.
No driver, HAL, kernel, video or APU implementation was changed.

The helper passed source waveform sanitizer checks and six capture-oracle cases,
actual NT5 import checks, and an ordinary emulator boot whose captured PCM showed
the exact left/right/both sequence twice with silence between phases. Emulator
results are recorded separately from user listening observations.

The new physical ticket used a fresh actual baseline capture and exact rollback.
Original startup, hives/companions, INF and audio files are restored; event/setup
history is retained. Inactive evidence paths /F/xwnaC01i, /F/xwnaC01p and the four
/E/Applications/XWNAC01scanB, XWNAC01scanI, XWNAC01scanP, XWNAC01scanR directories
remain preserved. Normal startup invokes none of them. Prior closed tickets and
physical FATX0101/video0093, original0088 and immutable0.1.0 were preserved.

## Records

- [Emulator qualification](../audio-channel001/emu001/audit.json)
- [Captured emulator sequence](../audio-channel001/emu001/capture.json)
- [Installation audit](install001/audit.json)
- [Physical playback audit](playback001/audit.json)
- [Restoration](restored001/restoration.json) and [final confirmation](restored001/confirmation.json)
- [Observations and evidence hashes](review001.json)
- [Closed successor ticket](queue-close.json)

The audio-channel001 physical ticket is closed with no active console operation.
This was a bounded test followed by rollback, not a permanent installation.
'''
(k/'REPORT.md').write_text(text)
closed={'owner':'audio-channel001','closed_utc':utc(),'baseline_restored':True,'report':str(k/'REPORT.md'),'declaration':'Fresh incoming baseline restored/read back; four allocation scans passed; final dashboard ownership verified.'}
with (state/'audio-channel001-closed.json').open('x') as f:json.dump(closed,f,indent=2)
(k/'queue-close.json').write_text(json.dumps(closed,indent=2)+'\n')
status={'owner':'audio-channel001','status':'complete-restored','updated_utc':utc(),'report':str(k/'REPORT.md'),'baseline_restored':True,'ticket_retained':False,'owned_sessions':[],'stereo_channel_mapping_verified':channel_verified,'user_observations':observations,'strict_whole_boot_passed':False}
for p in [state/'audio-channel001-status.json',state/'audio-status.json',k/'status.json']:p.write_text(json.dumps(status,indent=2)+'\n')
for link in re.findall(r'\]\(([^)]+)\)',text):assert (k/link).is_file(),link
(delivery/'audio-channel-report.md').write_text(re.sub(r'\]\(([^)]+)\)',lambda m:']('+str((k/m.group(1)).resolve()).replace('\\','/')+')',text))
(delivery/'audio-channel-review.json').write_text(json.dumps(review,indent=2)+'\n')
print('Physical channel case reviewed; incoming baseline verified; successor ticket closed')
