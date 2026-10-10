# PCI hardware220 â€” physical inventory complete; baseline restored

The October10 hardware220 handoff supersedes the historical coordinator-only
restriction. PCI is third, after restored-baseline audio and USB closures.
PCI claimed after both predecessor closures, launched one read-only inventory,
collected it after the user reported normal Restart and dashboard return, and
restored the original startup before collection. The reviewed physical diagnostic
passed; no functional SMBus/modem/AC97 qualification is claimed.

Current trial scope is live present-PCI identification and OS-assigned/boot resource
inventory only. The broader passive188 observer was removed from this trial after
two cold rehearsals reproduced its unreadable tail; those failures remain below.
The new user-mode
inventory queries Windows APIs only. It does not read/write PCI config directly,
touch SMBus/AC97/GPU registers, install services/drivers or manipulate dialogs.
Resource handles are released with CM_Free_*_Handle, never CM_Free_Log_Conf or
CM_Free_Res_Des, which would alter configurations. The original SMBus prototype
is not eligible for this physical trial while shared-bus ownership remains open.

Code: inventory.c. Preparation must compile against RosBE/NT5, verify actual
imports, rehearse in a fresh owned emulator fixture and cold-audit before physical
staging. Live OS resources cannot prove modem codec responsiveness. No functional
modem or physical SMBus qualification is implied by this first identification pass.

Upon queue grant: capture actual incoming boot/driver/startup and registry/event
state, verify FATX0101/video0093 and ownership marker, stage only uniquely named
user-mode helpers and a temporary startup, record one launch request, collect
after dashboard return, restore startup first and verify driver/service baseline.
Retain ownership if return/restoration requires user input. Close only through
queue.py with this absolute report path after verified restoration and dashboard.

Existing private connection details are available for process-local use. They
will not be stored in source/reports. Keyboard-unplugged authorization persists.
Build001 passed with the pinned RosBE compiler. The NT5 executable imports only
the reviewed query APIs from kernel32/setupapi; every import/forwarder resolved
against the pinned installed providers. Source and executable hashes are in
build001.json and build001-review.json. Eight simulated physical-protocol cases
passed, including ticket refusal, baseline drift, partial startup rollback and
uncertain launch handling (protocol001-tests.json). No simulator used sockets.

Emulator001 launched once at 05:25:54 UTC and closed at its 180-second host bound
at 05:28:54 UTC. The immutable source remains unchanged. Cold allocation and five
hive/header/history checks passed, but diagnostic_usable is **false**. Inventory
completed; result.txt is zero bytes and observer.log has a nontext tail beginning
at byte270337 of285046, during its fifth sample. Its final completion marker is
absent. Cause is not proven; no successful observer exit or persistence is claimed.
The closed runtime is retained and will never be relaunched.

Sixteen typed registry keys differ across both control sets (diagnosis.json).
Differences include physical-seeded versus emulator PCI resource vectors/BAR sizes,
IDE class01018Aâ†’010180 and IDE device checksum/timing data. These are real changes,
not an unchanged-binding PASS. No Service/Driver installation was performed by
the query-only helper. The inherited Ftdisk49 error remains a strict failure.

The complete NT5 inventory has12 present PCI devices. SMBus01B4 at0:1.1 has no
service/driver, problem1, no allocated log configuration and boot IO C000â€“C01F.
AC9701B1 at0:6.0 has the seed's ac97xnt5 binding;01C1 modem remains absent in xemu.
One NV2A descriptor reports type0/size0: its payload is explicitly unavailable,
not silently treated as success. Parser001 accepts the complete evidence while
preserving that limitation and rejects eight malformed/truncated variants.

Emulator002 is a fresh copy of the same immutable seed, unchanged helper binaries
and startup, with a360-second bound. It tests whether the observer finishes with
additional time; it cannot erase emulator001 or establish physical behavior.
It launched once at05:38:14UTC and closed at05:44:15UTC. Its runtime is closed,
source unchanged, and xemu lease released. Cold allocation/hive/header/history
checks passed again, but the observer has the same first nontext byte270337
(file length285047); only samples0â€“3 have completion records. Six minutes did not
resolve the tail failure. Both combined trials remain diagnostic_usable=false.
Underlying cause is unproven; no normal guest shutdown occurred in either run.

The empty result.txt has a reproduced command-parser cause: expansion of
`echo INVENTORY_EXIT %errorlevel%>file` with exit0 becomes input redirection `0>`.
Host Windows reproduces an empty file. Prefixing redirection (`>file echo ...`)
produces both expected records (cmd-redirection001.json). This host test is not
NT5 qualification. Emulator003 was prepared with corrected startup and the same
binary hashes. Its unlaunched lease waiter was stopped at the coordinator's
request to leave the next emulator window for root221; no guest was interrupted.
It is now closed without launch, superseded by inventory-only emulator004.

After root221 completed and released its leases, fresh emulator004 launched the
unchanged reviewed inventory alone with corrected command redirection and a
180-second host bound. It stages no passive188 observer. It launched at05:51:28UTC
and closed at05:54:28UTC. Cold audit passed diagnostic_usable: complete inventory,
`INVENTORY_EXIT 0`, exact protected files, five parsed/checksummed/sequence-consistent
hives, retained SetupAPI/event history,319 directories/6717 files/320 directory
clusters with no orphan or allocation error. Both failed combined trials remain
unchanged. No active PCI guest or lease remains.

Binding_state_unchanged is deliberately false. The exact typed delta matches the
reviewed/pinned emulator001 physical-seedâ†’emulator transition; that narrow match
is sufficient for query-helper rehearsal only. No broad metadata exclusion or
physical-baseline waiver is used. Physical returned-state checks compare all selected configuration and hold
any differences for explicit review, as documented below. The inherited Ftdisk49 and absent normal shutdown keep
whole-boot/hardware/persistence qualification false.

The physical harness requires this successful emulator004 audit, fresh incoming
physical preflight and the serialized console ticket. Protocol003 repeats all
eight launch/rollback simulations for the inventory-only harness. Previous
protocol source bytes and results remain separately pinned.

PCI claimed the queue after both restored predecessor closures. Physical001
captured the actual incoming startup, five hives, event/SetupAPI/trace files and
17 protected boot/driver/provider files. Protected hashes and all hive checks
passed preflight. One inventory-only launch was accepted at2026-10-10T15:45:23.634370+00:00.
The user was asked to use normal Windows Restart after the command window closes.
Dashboard return was collected at15:48:02UTC. Startup was restored and read back
first at15:47:58UTC; the temporary inventory startup is no longer enabled.
No functional SMBus/AC97/GPU writes or driver installation occurred.
The queue's private pci-status.json links this report; predecessor state is untouched.

Physical offline preflight validates all five captured hives and protected
incoming payloads before staging. Returned-state audit compares complete typed
Enum, Services, Class, DeviceClasses, Video, CrashControl and Select state;
differences hold baseline closure for review. It also checks exact startup and
protected bytes, new event boundaries, retained SetupAPI history and inventory
completion/exit records. No whole physical allocation audit is available through
these file captures. Normal shutdown requires separate actual observation;
EventLog6006 or reachable dashboard FTP alone does not establish it.

Primary API references:
- https://learn.microsoft.com/en-us/windows/win32/api/cfgmgr32/nf-cfgmgr32-cm_get_first_log_conf
- https://learn.microsoft.com/en-us/windows/win32/api/cfgmgr32/nf-cfgmgr32-cm_get_next_res_des
- https://learn.microsoft.com/en-us/windows/win32/api/cfgmgr32/nf-cfgmgr32-cm_free_log_conf_handle

## Physical001 result and restoration review

The complete inventory enumerated **14 present PCI devices** with `INVENTORY_EXIT 0`.
The user explicitly reported: "Restart completed; Xbox dashboard is visible".
A new EventLog6006 record333 corroborates the normal restart observation. This was
one launch, accepted at15:45:23UTC; no retry or forced reset occurred. An initial
refused collection connection is preserved in physical001-collection-attempt001.json.

| Physical device | Location | Live Windows result |
| --- | --- | --- |
| SMBus10DE:01B4 revB1 |0:1.1| Problem1; no service/driver or allocated configuration. Boot I/O C000â€“C00F and C200â€“C21F. |
| Modem10DE:01C1 revB1 |0:6.1| Present; problem1; no service/driver, allocated or boot configuration. |
| AC9710DE:01B1 revB1 |0:6.0| Existing ac97xnt5 binding; problem10; no allocated or boot configuration. |

These are live SetupAPI/Configuration Manager observations, not direct BAR or
codec transactions. Missing Windows resources do not establish missing hardware
BARs. The modem's presence and SMBus resource ranges differ from xemu: its rehearsal
had12 present devices, no01C1, and one SMBus boot range C000â€“C01F. Functional modem
support and safe SMBus ownership remain unresolved. NV2A also returned one type0,
size0 resource descriptor; its payload remains explicitly unavailable.

The original startup and all17 protected boot/driver/provider files are byte exact.
All five before/after hives parse and have valid headers/checksums/sequences.
SetupAPI and both event histories are preserved. The initial strict full selected
configuration comparison deliberately remains **false** in physical001-audit.json.
Its collected manifest remains byte exact in physical001-collected.json, matching
the original audit's record hash.

The separate reproducible review (review-physical001-restoration.py and
physical001-restoration-review.json) accepts only20 changed runtime values across
8 exact keys in ControlSet001/002: four lease times in each of two network paths,
one binary DHCP cache, and one LanmanServer Guid per control set. Lease times all
advance70255 seconds, keeping the86400-second lease and T1/T2 intervals unchanged.
Only10 explicit expiry DWORD offsets change in each cache; every other cache byte
and network setting is exact. Both server identities are v4 UUIDs. The independently
captured USB220 before/after SYSTEM hives show the same old server identity becoming
a different v4 identity during that earlier boot, without this PCI helper. This
supports the boot-runtime interpretation; it is not a claim about NT5 internals.
No broad service-subtree exclusion was applied, and no registry value was rewritten.
All other selected Enum, Services, Class, DeviceClasses, Video, CrashControl and
Select values are unchanged. Baseline restoration is accepted within that explicit
scope, not as byte equality of the complete hives.

A new inherited Ftdisk49 error remains in system event328, HarddiskVolume6.
SetupAPI appended3222 bytes, including no-compatible-driver0xe0000228 results for
APU01B0, SMBus01B4, modem01C1 and USB Vid_ffff/Pid_ffff. The helper installed no
driver, changed no device configuration and acted on no dialog. These results
remain failures for general hardware/whole-boot qualification; they do not invalidate
the completed identification log. No complete physical allocation scan or repeated
boot durability test was performed. Failed observer rehearsals remain preserved.

The unique /F/xwnpci220a helper/backup/log directory remains as evidence. Normal
startup is restored. The next engineering question is supported driver ownership
and hardware resource handling; this trial authorizes no functional register writes.

PCI ticket closed through queue.py at2026-10-10T15:53:37.950079+00:00 after
verified restoration and dashboard return. No PCI process, guest or lease remains.

Validation: the offline restoration review and evidence-hash chain passed;
`git diff --cached --check` passed; tools/check-repository.py passed binary/media/
credential-pattern checks for19423 tracked files.
