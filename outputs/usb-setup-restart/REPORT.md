# Identified setup guard cleared; assisted guest restart and cold integrity pass

Fresh emulator case nt5setup-emu001 completed a guest-requested normal restart,
returned to the dashboard, and passed the scoped cold-integrity checks. The
strict event gate remains false because of Ftdisk event 49. This was an assisted,
instrumented diagnostic: unassisted reboot and physical hardware remain unqualified.
No guest driver, kernel, HAL, loader or physical baseline was changed.

Five read-only observer samples over 126,195 ms consistently identified PID 916
running newdev.dll,DevInstall for the exact NVIDIA VEN_10DE&DEV_01B0 instance,
with a visible, enabled Found New Hardware Wizard welcome page. The setup API
returned WAIT_TIMEOUT at both ends of every sample. This matches the preceding
closed SetupAPI evidence, which reported no compatible driver (0xe0000228).
The live observer preserved command lines, full child-control text and device
metadata before any action. Its 70 unavailable-property results per sample
(error 13) remain in the record; they were not converted to successful queries.
See [live identification](emu001/setup-evidence.json),
[all observer samples](emu001/observer-analysis.json) and
[prior SetupAPI delta](parent-setupapi-delta.txt).

The unchanged helper then verified and canceled four known welcome dialogs:

| Target | Exact device identity (instance suffix retained in evidence) | PID |
| --- | --- | --- |
| 1 | PCI VEN_10DE, DEV_01B0 | 916 |
| 2 | PCI VEN_10DE, DEV_01B4 | 912 |
| 5 | PCI VEN_1B36, DEV_0005 | 276 |
| 6 | USB VID_045E, PID_0202 | 280 |

Every target was present in the pre-action device inventory. Each action checked
the complete command/instance, original process creation identity, exact welcome
text, parent/control ownership and foreground/active state immediately before
BM_CLICK on Cancel. Each corresponding window closure was observed. Four actions,
joined helper exit zero, helper idle for 5,100 ms and another 5,100 ms of probe
setup idle all passed. The last install check returned zero immediately before
ExitWindowsEx. No gate was waived, unknown dialog dismissed or device disabled.
Cancel acknowledges an unsupported installation; it does not install a driver
or prove controller support. See [helper log](emu001/wizard201.log.txt),
[probe log](emu001/status2.log.txt) and [qualification](emu001/qualification.json).

The single Windows launch was accepted at 01:20:30.603 UTC on 2026-10-11
(9:20:30 p.m. EDT on October 10). Dashboard return occurred 218.897 seconds later.
The cold event log contains exactly one new normal-shutdown event. After dashboard
return, HMP stop/quit closed the emulator with exit code zero at 01:24:10.129 UTC;
the runner did not use Kill. The expected monitor reset after quit was recorded
and accepted only in that quit response. Root phase237's three-case matrix was
closed before this launcher acquired its exclusive xemu/xemu-ui leases.

| Cold check | Result |
| --- | --- |
| Protected system files and staged probe binaries | Exact |
| Deterministic payload | All 2,226 bytes exact |
| Probe status and exit | Parsed; exit zero (ASCII 0, space, CRLF) |
| Full allocation scan | Consistent; zero orphan clusters |
| SYSTEM, SOFTWARE, DEFAULT, SAM, SECURITY | Header/checksum/sequence and full traversal pass |
| Prior event and SetupAPI history | Preserved |
| Selected service/policy state | Unchanged; no new device disabling |
| XID driver and registry references | Absent |
| Independent reads | Full file/hive/FAT views and 148 selected clusters agree |
| Final submitted bytes in eight selected targets | All exact; no overlapping in-flight writes |

See [cold audit](emu001-review.json), [hive/event details](emu001/details.json),
[typed device state](emu001/device-state.json),
[independent forensics](emu001/forensics.json) and
[write-to-cold comparison](emu001/transfer-cold-comparison.json).
The natural hub metadata changes are retained: hub LocationInformation/DeviceDesc
changed and ConfigFlags 1024 became zero. These are not evidence that every
unsupported device acquired a working driver.

The capture contains 20,511 complete, uniquely matched DMA/backend request pairs.
All DMA and backend completions returned zero, all four endpoint snapshots agree,
and no records were capped, missing, unmatched or pending. All observed successful
final writes to the three probe files and five hive targets equal cold bytes;
untouched bytes are outside that write-comparison denominator. The three saved
QCOW mappings are present. The complete run contains 18 IDE FLUSH CACHE EXT
(0xea) commands; this count alone does not attribute them to individual probe
FlushFileBuffers calls or prove power-loss durability. Endpoint agreement does
not exclude transient changes between snapshots. See
[transfer summary](emu001/transfer-analysis.json),
[phase differences](emu001/phase-differences.json) and
[mapping/command evidence](emu001/qcow-evidence.json).

The large derived JSON arrays were split losslessly into bounded text parts.
Their manifests retain row counts, part hashes and original hashes; reconstruction
was compared to every original row. Exact original JSON bytes remain private.
The post-collection chunking step and clarification of the mapping analyzer's
scope do not change runtime evidence; exact prelaunch scripts remain frozen.

The only new guest binary is the probe wrapper: SHA-256
266ef08400f94c05195289d4b47a2202c1c400a7254054f5c73f558de25e3e38.
It adds the joined read-only observer and enables the existing helper before the
unchanged setup/restart gates. The helper is byte-exact at 33558f1c...f19eb9;
the observer remains d69deda0...be1487; their full hashes, imports and source pins
are recorded in build-review.json, unchanged-guards.json and prelaunch-emu001.json.
All 390 helper-policy checks passed. The emulator remains the instrumented
5070031b...fd36 build from cda0476; parent image remains 6de11f0c...584f97.

The earlier forced-stop mapping-loss image and orderly-host-exit control remain
separate and unchanged. This successful guest restart does not retroactively
repair or qualify either, or the older hive failures. Raw media, hives, binaries
and buffers stay private on E:. Both emulator leases and the cold-audit build
lease are released. No new guest is queued. See [NEXT.md](NEXT.md) for remaining work.
