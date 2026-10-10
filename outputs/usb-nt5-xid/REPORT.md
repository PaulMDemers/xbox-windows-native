# NT5 XID emulator input result

Windows 2000 SP4 installed the experimental XID driver in xemu and exposed a
HID-compliant game controller. The probe passed 200 HID reads across two
open/read/close cycles. This establishes an emulator input smoke test; normal
restart, lifecycle behavior, deliberate controls and physical use remain unqualified.

## Build and host checks

Build032 compiled the original driver and probe using the pinned RosBE i386
GCC 8.4 toolchain with warnings treated as errors and NT5 subsystem versions.
Actual linked imports were checked against the preserved NT5 providers, including
the Xbox HAL. See `build032.json` and `build032-review.json`.

- Driver SHA-256: `6d5ffc5de55c6ca304713ade7b438675744ccb81d0510e0d2810c3ecbe2abeb2`.
- Probe SHA-256: `b833cfe764acd134a8748e8c90b3c6be858616b2df41b2a2cbd5fd31a77a2507`.
- 78,915 executed HID mapping/descriptor checks passed (`hid-tests.json`).
- Nine deterministic schedules of the actual USB wait/cancel function passed
  (`transport-tests.json`). These are isolated function tests, not concurrency
  or complete PnP validation.

The INF and runtime device guard accept only xemu's 045e:0202. The driver, codec,
INF and probe sources are unchanged from source-only checkpoint d8b45d2.

## Observed emulator behavior

Emu001 used a private overlay over seed SHA-256
`7c09d05af676a7c37f242850837a8b2fa19b81a6ae63b2af2ec156e9a5fa197b`.
The owned host process started at 2026-10-10 20:05:59 UTC; exactly one Windows
launch was accepted at 20:06:29 UTC. No deliberate controller input was injected.

Installation returned success. HID parsing reported usage page 1, gamepad usage
5, 13-byte input reports, no output report, one button capability and six value
capabilities. Both cycles completed 100 reads. The four logged raw samples were
neutral. Cached HID reads do not establish 200 independent USB transactions or
physical input mapping. See `emu001/probe.txt` and `emu001-review.json`.

Cold registry inspection found the USB device bound to service `xwnxid`, driver
entry 0025, and its HID child registered as a HID-compliant game controller,
entry 0026. SetupAPI recorded successful parent and child installation. The raw
last-error value 0x103 was recorded after a successful install return and is not
an installation failure. Unsigned-INF warnings remain in the evidence.

## Restart and event limitations

The pending-install check returned 0x102. The helper deliberately held restart
and exited with code 2. The external watchdog stopped the owned host process at
20:10:30 UTC. There was no dashboard return or EventLog 6006 shutdown record.
The captured desktop was scrambled and cannot establish the visible wizard or
interactive gamepad behavior.

SetupAPI also recorded an unmatched NVIDIA APU device and a new-device wizard.
The exact pending window was not established. A fresh diagnostic must identify
it before a normal-restart trial; this record does not attribute the hold solely
to the APU.

Strict event checks failed: new records include DCOM 10005, Ftdisk 49 and
PerfDisk 1000. Their cause is unresolved and has not been attributed to XID.
See `emu001/events.json` and `emu001/setupapi-delta.txt`.

## Cold integrity and cleanup

All 32 protected, staged and installed-file checks were byte exact. Five registry
hives passed header/checksum/sequence checks and full traversal. Complete F:
allocation audits found zero errors and zero orphan clusters before and after
the run (6,716 to 6,723 files); existing bad-cluster fixture markers were retained.
Historical event and SetupAPI prefixes were preserved.

The first deep-audit attempt failed because the host could not locate its private
libhivex library. The corrected library search path parsed the same captured
files, without relaunching or recollecting the guest. The initial failure is
retained in `emu001-audit-initial-failure.json`.

All USB-owned emulator sessions and leases are closed. The physical Xbox and
shared baseline were not accessed or changed during this follow-up.

## Next qualification steps

1. Identify the pending installer in a fresh private diagnostic, then demonstrate
   normal restart and a subsequent boot with independent cold inspection.
2. Exercise cancellation, stop/removal and device-power transitions. The current
   experimental driver vetoes query-stop/remove while started; it needs proper
   transition handling before general or physical release.
3. Prepare a separate physical device package only under a fresh serialized
   hardware ticket, with baseline capture and attended control labels.

The harness separates `Prepare.ps1` (build lease), `Run.ps1` (exclusive emulator
and UI leases), and `Audit.ps1` (build lease). Every guest attempt requires a
fresh case ID. Do not relaunch emu001 or treat a host stop as normal shutdown.

`runtime-manifest.json` freezes the current evidence. `freeze.json` describes the
historical source-only checkpoint; its exact original report is preserved as
`SOURCE-ONLY-REPORT.md` and linked by `history.json`. The harness input record
explicitly states that it was captured after host start.
