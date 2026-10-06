# Isolated FATX0098 physical trial

This trial changes only the filesystem driver from 0088 to 0098. Baseline 0093
miniport, Microsoft framebuf.dll, HAL, loader and mode remain unchanged. The
trace file is not reseeded; normal runtime trace updates are preserved.
The API-only probe creates 17 input files in C:\xwneof98, maps and reads them,
then performs 136 output write/flush/close/reopen/mapping cycles across the same
sector/page/cluster boundary sizes as the paired emulator regression. It waits
two minutes and requests a normal restart. It never writes raw FAT metadata.
Hardware input slack is not claimed to be deliberately nonzero.

The new probe is derived from the recorded mapped-EOF source. Its executable,
imports, compiler and source hashes are pinned in build-review.json. Rehearsal
uses one owned xemu overlay with exactly the physical baseline video binaries
and FATX0098; inherited emulator hardware/registry differences remain explicit.

physical.py check reads the physical baseline. deploy-launch requires the explicit controlled-trial
eligibility report, verifies baseline again, preserves originals locally and on F:,
stages/readbacks one unique probe directory and candidate driver, then records
one launch before sending it. It refuses a second deployment under the same ID.
If prelaunch staging fails, it attempts the original startup/driver restoration.
collect restores ordinary startup first and preserves all trial files and logs.
rollback restores 0088 without launching Windows. No new video binary is uploaded.

watch.py observes return without launching. scan.py stages the previously
qualified read-only allocation helper in a unique E: directory and launches it
once after Windows collection; its outputs are on E:, its F: handle is read-only.
audit-binaries.py checks all 3439 manifest binaries and nine registry hives.
qualify.py keeps workload/event qualification separate from allocation/binary
checks until all are complete. A dashboard return, visible desktop or old report
alone is not qualification. Credentials are required through XWN_FTP_HOST,
XWN_FTP_USER and XWN_FTP_PASSWORD; they are not saved in these files.

Statuses are in preflight.json, rehearsal*/audit.json, eligibility.json, physical.json,
windows-return.json, scan.json, allocation.json, binary-audit.json and
qualification.json as they become available. Missing reports mean pending work.
Candidate0098 must not be described as a long-soak or video-performance pass
from this bounded trial. Release0.1.0 and recovery bundles stay intact.

## Physical result: PASS

The one Windows trial launched at 2026-10-06 01:46:56 UTC and returned normally
at 01:50:47 UTC. It passed 153/153 mapping checks, 136 output write/flush/reopen
cycles and all 34 independent file-content comparisons. Collected event logs
show a normal shutdown, no new application events, no popups and no unexpected
warning/error events. Input slack was not deliberately poisoned on hardware.

The subsequent read-only allocation scan found 122,181 files and 6,066
directories, with no crosslinks, orphan clusters or capture/chain errors.
All 3,439 manifest binaries match; all nine captured registry hives pass header
checks and reachable key/value traversal. This is not registry semantic validation.
See [qualification](qualification.json), [allocation](allocation.json),
[binary/hive audit](binary-audit.json) and [final console state](final-state.json).

Normal startup is restored, FATX0098 remains installed, and baseline video0093,
framebuf.dll, HAL and loader are unchanged. FATX0088 and original startup are
preserved locally and under F:\xwneof98 for rollback. All owned processes are
closed. The trial does not establish long-soak or video-performance stability.
Next coverage is desktop save/reopen and a longer soak using fresh attempt IDs.

## Rehearsal distinction

The first rehearsal completed 153/153 checks, persisted all 34 files and logged a
normal guest shutdown, but xemu became unresponsive during an HMP framebuffer
read. That run was forcibly closed and fails the dashboard-return gate. The
unchanged second rehearsal, without capture, returned to dashboard and passed
all storage/content/hive/payload checks. It logged the shutdown-time rundll32
installer popup also present in the old0088 control; its strict emulator gate
remains FAIL. Neither failure has been erased or reclassified as a clean boot.

eligibility.json allows the already-authorized isolated physical trial based on
the prior clean paired0098 regression and the new probe's confirmed storage and
normal-restart results. This does not identify the popup's cause or waive a
physical popup. Physical qualification independently requires clean event and
payload/allocation/hive checks. All emulator processes are closed.
