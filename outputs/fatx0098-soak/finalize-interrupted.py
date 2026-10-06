"""Record a clean post-restart integrity audit without promoting the interrupted soak."""
import json,hashlib,datetime
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
read=lambda name:json.loads((k/name).read_text())
q=read('qualification.json');b=read('binary-audit.json');a=read('allocation.json');s=read('installed-state.json');manual=read('manual-discovered-audit.json');interrupted=read('interruption.json')
assert not q['passed'] and not interrupted['final_completion_marker_present']
assert b['complete'] and b['passed'] and b['checked']==3439 and len(b['hives'])==9
assert all(h['tree']['passed'] and h['matching_sequences'] and h['checksum_valid'] for h in b['hives'])
assert a['allocation_consistent'] and s['passed'] and manual['passed']
assert interrupted['all_527_mapping_checks_passed'] and interrupted['all_50_final_files_match']
r=dict(scope=__doc__,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),strict_soak_passed=False,classification='Timed soak interrupted; observed operations and post-restart integrity passed',mapping_checks_passed=527,exact_automated_files=50,synthetic_bmp_save_replays=16,deleted_intermediates_absent=34,last_logged_elapsed_ms=840000,required_elapsed_ms=900000,normal_eventlog_stop=True,automatic_restart_request_present=False,manual_file_audit=manual,allocation_files=a['files'],allocation_directories=a['directories'],binary_hashes=3439,structural_hives=9,original_startup_restored=True,drivers_unchanged=True,original0088_rollback_intact=True,recovery_snapshot_created=False,recovery_snapshot_reason='Full timed-soak qualification did not pass; existing0.1.0 archives are preserved.',processes_running=[],next='A fresh timed run must reach its own completion/automatic restart marker before the full soak can pass; no Windows relaunch in this attempt.',evidence_sha256={name:hashlib.sha256((k/name).read_bytes()).hexdigest() for name in ['qualification.json','interruption.json','manual-discovered-audit.json','allocation.json','binary-audit.json','installed-state.json','warning-comparison.json']})
(k/'summary.json').write_text(json.dumps(r,indent=2)+'\n')
head=r"""# Continuation: FATX0098 interrupted soak audited; console on dashboard

Latest: outputs/fatx0098-soak. The user restarted during the final timed wait.
Normal EventLog shutdown is recorded. All527 mapping checks,16 synthetic BMP
save replays,50 exact automated files and34 deleted intermediates passed, but
only14 timed markers (840000ms) and no COMPLETE/automatic restart marker exist.
The full15-minute soak remains INCOMPLETE, not a driver failure or full PASS.
No Windows relaunch was made. Do not reuse these trial/scan IDs.

Post-return allocation audit:122248 files,6069 directories,zero errors/orphans.
All3439 manifest binaries match; nine hives pass header and key/value traversal.
No new application events/popups. Three Srv2013 warnings exactly match previous
records; strict qualification preserves them. No gate was weakened to claim PASS.

User-saved C:\xwns98\manual-apint.bmp (961x532 RGB,1534342 bytes) decodes fully;
C:\xwns98\manuel-note.txt (27 ASCII bytes) was read back after reboot. Exact
hashes and user observations are separate reports. User reports apps opened/
closed, saves, Pinball and an OpenGL application running, with apparently faster
window redraw still visibly filling top-to-bottom. Actual UI reopen success,
measured speedup and hardware OpenGL acceleration are not established.

Normal startup restored. FATX0098/video0093/framebuf/HAL/loader are unchanged;
original0088 rollback remains at/F/xwneof98/rollback.sys. installed-state.json
verifies these independently of the failed timed gate. All owned emulators,
observers, scan and audit processes are closed. New recovery capture was not run
because its full-soak PASS prerequisite was not met;0.1.0 bundles/tag intact.

Next: a fresh timed soak with its own completion and automatic restart evidence,
then updated recovery capture and the separate video plan. No additional Windows
run belongs to this attempt. Pause the follow-up automation after committing.

## Historical continuation

"""
p=ws/'outputs/engineering-notes/CONTINUATION.md';old=p.read_text();marker='# Continuation: FATX0098 passes the bounded physical trial';assert marker in old;p.write_text(head+old[old.index(marker):])
p=k/'README.md';text=p.read_text();text=text.replace('Status: physical launch accepted at 2026-10-06 02:06:48 UTC; result pending.','Status: physical run returned after user restart; timed soak incomplete. See summary.json and the result below.')
text+=r"""
## Collected result: interrupted timer, clean observed storage and integrity

The user reported restarting; dashboard return was observed at02:23:36UTC.
All527 mapping checks completed with zero content/tail failures,16 synthetic BMP
save sequences passed, all50 final automated files match, and all34 intermediate
paths are absent. Only14 timed completion markers were written; the last reports
840000ms. The final900000ms marker, COMPLETE and automatic restart request are
absent. This is not a full fifteen-minute pass, and it is not a demonstrated
driver failure. The strict qualification remains false.

Normal event-log shutdown is present; no application events or popups were added.
Three Srv2013 warnings exactly match earlier records (warning-comparison.json),
and remain in the strict result. Post-return allocation is consistent across
122248 files/6069 directories with zero orphans/errors. All3439 binaries and nine
structural hive audits pass. installed-state.json confirms normal startup,0098/
0093 baseline hashes and the original0088 rollback. No further Windows run or
PASS-gated recovery capture occurred. The original0.1.0 archives remain intact.

The user's files used different names: manual-apint.bmp and manuel-note.txt in
C:\xwns98. Both were collected; the961x532 RGB bitmap decodes fully and the text
contains27 ASCII bytes. Their hashes are in manual-discovered-audit.json.
This preserves the original suggested-name audit, which correctly found those
suggested names absent. Application/UI observations remain user-reported;
synthetic save replay and cold file checks do not prove hardware acceleration
or a measured window-drag speedup.
""";p.write_text(text)
(ws/'EMULATOR-SESSION.txt').write_text('FATX0098 soak audited after user restart. Full timed gate INCOMPLETE (14 markers, no final completion); all observed storage/manual file checks and cold integrity pass. Normal startup restored, no owned processes running. Xbox dashboard,0098/0093 unchanged,0088 rollback intact. See outputs/fatx0098-soak/summary.json. No new Windows launch.\n')
print('Interrupted result finalized without changing strict qualification')
