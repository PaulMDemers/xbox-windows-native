"""Review closed-case evidence, document observations, then release this successor ticket."""
import ast,datetime,hashlib,json,pathlib
k=pathlib.Path(__file__).resolve().parent
repo=k.parents[1]
state=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-hardware220/state')
out=pathlib.Path('C:/Users/Paul/Documents/Codex/2026-10-09/xbox-windows2000-audio/outputs')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
utc=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
assert not (state/'audio-listen001-closed.json').exists()
frozen=read(k/'frozen001.json')
for p,h in frozen.items():assert sha(pathlib.Path(p))==h,p
for p in k.glob('*.py'):ast.parse(p.read_text())
audits={c:read(k/c/'audit.json') for c in ['install001','playback001']}
assert audits['install001']['scoped_installation_passed']
assert audits['playback001']['scoped_runtime_passed']
for c,r in audits.items():
 assert r['normal_shutdown_count']==1 and r['dashboard_return'] and r['integrity_passed']
 assert {(v['source'],v['event_id']) for v in r['warnings_errors']}=={('Ftdisk',49)}
 assert not r['strict_qualification_passed']
for c in ['baseline001','install001','playback001','restored001']:
 a=read(k/c/'allocation.json')
 assert a['allocation_consistent'] and not a['errors'] and a['orphan_cluster_count']==0
restored=read(k/'restored001/restoration.json');confirmed=read(k/'restored001/confirmation.json')
assert restored['completed'] and restored['baseline_restored'] and all(restored['checks'].values()) and confirmed['passed']
observations=[read(p) for p in sorted(k.glob('user-observation*.json'))]
assert observations and observations[0]['audible_output_observed']
tone=next((r for r in observations if r.get('case')=='playback001'),None)
evidence=['capture002.json','before-audit002.json','providers001.json','frozen001.json','install001/audit.json','playback001/audit.json','restored001/restoration.json','restored001/confirmation.json']
evidence+=[str(p.relative_to(k)) for p in sorted(k.glob('user-observation*.json'))]
review={'passed':True,'reviewed_utc':utc(),'frozen_inputs_verified':len(frozen),'python_sources_parsed':len(list(k.glob('*.py'))),'evidence_sha256':{n:sha(k/n) for n in evidence},'physical_runtime_passed':True,'user_heard_windows_login_sound':True,'dedicated_tone_observation':tone,'stereo_channel_mapping_verified':bool(tone and tone.get('stereo_channel_mapping_verified')),'instrumented_capture':False,'strict_whole_boot_passed':False,'strict_failure':'Ftdisk49','baseline_restored':True,'restored_readback_files':len(restored['checks'])}
(k/'review001.json').write_text(json.dumps(review,indent=2)+'\n')
text=f'''# Xbox analog audio listening result

The user heard the Windows login sound through speakers connected to the
composite cable audio connectors. The unchanged build004 driver also passed
genuine installation and a subsequent twelve-cycle playback/reset test on the
physical Xbox. The captured incoming baseline has been restored and verified.

## What the evidence establishes

| Evidence | Result |
| --- | --- |
| User listening observation | Windows login sound heard during installation; reboot observed. |
| Genuine installation | Exact ACI device, SetupAPI success, xwnaci207 binding, problem 0. |
| Subsequent playback boot | xwnaci207 loaded, legacy module absent, twelve cycles passed; eight full 96,000-sample plays and four reset-shortened plays. |
| Shutdown | Joined helpers, unforced restart, one new EventLog6006 and dashboard return on each Windows boot. |
| Cold integrity | Five hives, protected bytes, event/setup history and policy checks passed on both boots. |
| Allocation | Before Windows, after installation, after playback and after restoration: zero errors/orphans. |
| Restoration | {len(restored['checks'])} readback checks; {len(restored['writes'])} changed files restored and {len(restored['removed'])} exact new files removed after preservation. |
| Strict whole-boot qualification | FAIL: Ftdisk49 on both Windows boots; never waived. |

The listening observation is separate from the driver's runtime evidence.
The login sound occurred with build004 staged under the incoming legacy filename,
before or during the genuine SetupAPI installation; the subsequent playback boot
independently verified xwnaci207 service and module ownership.
'''
if tone:
 text+='\nDedicated playback observation: '+tone['user_report']+'\n'
else:
 text+='\nNo user observation of the dedicated tone pattern was received before closure. Correct left/right routing and measured signal quality remain unverified.\n'
text+='''
No instrumented audio capture was made. APU, digital/S/PDIF/HDMI output, capture,
hardware mixer controls, protected content and suspend/resume remain unqualified.
Known unrelated wizard cancellation means these were not prompt-free boot tests.
Later emulator storage failures remain separate unresolved evidence; these
bounded physical results do not establish general repeated-boot storage safety.

## Candidate and rollback

Driver version 0.0.4.207, SHA256
`c5736457d9f4b7c6dafc730eb19bc0eda6c6820cee8e21580d357708df36cd75`.
Source/package commit `7cdb191bd2ef72e24001370726f97a7383a7250b`.
No driver, helper, HAL, kernel, video or APU implementation changes were made.

A fresh capture saved and double-read 1,223 actual incoming files. The five
hives passed traversal and header checks; 11 actual providers and three native
export tables passed. The fresh capture, rather than an older trial's registry,
was used for restoration. Original startup, hives/companions, INF and audio files
are restored. Event and SetupAPI history are retained.

New inactive evidence directories are /F/xwnaL01i, /F/xwnaL01p and
/E/Applications/XWNAL01scanB, scanI, scanP, scanR (each with the XWNAL01 prefix).
Normal startup invokes none of them. Original0088, physical FATX0101/video0093,
immutable0.1.0 and prior closed evidence were preserved.

## Records

- [User observation](user-observation001.json)
- [Installation audit](install001/audit.json)
- [Playback audit](playback001/audit.json)
- [Restoration](restored001/restoration.json) and [final confirmation](restored001/confirmation.json)
- [Review and evidence hashes](review001.json)
- [Controller provenance](controller-provenance.json) and [frozen inputs](frozen001.json)
- [Successor ticket closure](queue-close.json)

The new audio-listen001 ticket is closed after verified restoration and dashboard
return. No active physical session remains. The original hardware220 ticket was
never reopened. This test did not permanently install the candidate or promote a
combined device/video fixture.
'''
(k/'REPORT.md').write_text(text)
(out/'audio-listening-report.md').write_text(text.replace('](',']('+str(k).replace('\\','/')+'/'))
(out/'audio-listening-review.json').write_text(json.dumps(review,indent=2)+'\n')
closed={'owner':'audio-listen001','closed_utc':utc(),'baseline_restored':True,'report':str(k/'REPORT.md'),'declaration':'Incoming baseline/startup restored and read back; four allocation scans passed; dashboard confirmed; no active physical operation.'}
with (state/'audio-listen001-closed.json').open('x') as f:json.dump(closed,f,indent=2)
(k/'queue-close.json').write_text(json.dumps(closed,indent=2)+'\n')
status={'owner':'audio-listen001','status':'complete-restored-audible-login-observed','updated_utc':utc(),'report':str(k/'REPORT.md'),'baseline_restored':True,'ticket_retained':False,'owned_sessions':[],'audibility_observed':True,'audibility_scope':'User heard Windows login sound; see dedicated observation field','dedicated_tone_observation':tone,'strict_whole_boot_passed':False}
for p in [state/'audio-listen001-status.json',k/'status.json']:p.write_text(json.dumps(status,indent=2)+'\n')
print('Evidence reviewed; incoming baseline restored; new listening ticket closed')
