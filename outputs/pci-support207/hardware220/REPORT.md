# PCI hardware220 — inventory rehearsal passed; console queue not granted

The October10 hardware220 handoff supersedes the historical coordinator-only
restriction. PCI is third, after restored-baseline audio and USB closures.
Initial `queue.py claim pci` returned WAIT for audio. Audio subsequently claimed.
No console connection, deployment, launch or physical observation has occurred.

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
IDE class01018A→010180 and IDE device checksum/timing data. These are real changes,
not an unchanged-binding PASS. No Service/Driver installation was performed by
the query-only helper. The inherited Ftdisk49 error remains a strict failure.

The complete NT5 inventory has12 present PCI devices. SMBus01B4 at0:1.1 has no
service/driver, problem1, no allocated log configuration and boot IO C000–C01F.
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
(file length285047); only samples0–3 have completion records. Six minutes did not
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
reviewed/pinned emulator001 physical-seed→emulator transition; that narrow match
is sufficient for query-helper rehearsal only. No broad metadata exclusion or
physical-baseline waiver is used. Physical returned-state checks still require
unchanged configuration. The inherited Ftdisk49 and absent normal shutdown keep
whole-boot/hardware/persistence qualification false.

The physical harness requires this successful emulator004 audit, fresh incoming
physical preflight and the serialized console ticket. Protocol003 repeats all
eight launch/rollback simulations for the inventory-only harness. Previous
protocol source bytes and results remain separately pinned.

No physical claim is held. The queue's private pci-status.json links this report;
predecessor state is untouched.

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
