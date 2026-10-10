# PCI SMBus follow-up — 2026-10-10

The resource-only driver now installs and starts correctly in NT5. A fresh
emulator run passed device restart, six real D3/D0 power transitions, safe removal
and re-enumeration. Normal Windows restart is still held by pending setup258;
the appended SetupAPI history names audio01B0. No setup cancellation or device
disable was used. This is a resource/lifecycle milestone, not hardware readiness.

Two concrete compatibility failures were fixed: the validator now accepts the
captured NT5 START resource encoding (0/0 header,0x31 I/O flags) while preserving
exact address/length/type/count restrictions; the removal probe now uses the
implemented Unicode API because the pinned ANSI export is a constant stub.
The power path also delays NT5 readiness until its state update is complete and
uses a preallocated work item/context for device SET_POWER. Functional telemetry
remains disabled in every new lifecycle trial.

The separate HAL candidate implements a shared nonblocking SMBus owner and a
bounded terminal takeover. Its65,894 compiled ASan/UBSan model cases pass, including
16 takeover boundaries; the native HAL compiles and its imports, exports and
resident terminal code pass static review. It has not been booted. The reconstructed
control HAL is not byte-identical to the installed baseline; recorded source-path
and section-layout differences require control/candidate native validation before
promotion. Finite polling cannot guarantee recovery from a stuck physical bus.

The resource policy passes5,751 sanitizer cases. All four closed lifecycle trials
pass their cold protected-file, hive, log-history and FATX allocation checks.
Actual PnP tracing confirms query-remove/remove/start events, but STOP and cancel
paths were not observed. Normal shutdown, two ordinary cold boots, complete
configuration equality and strict whole-boot success remain unqualified; inherited
Ftdisk49 remains a failure. No physical-console access or deployment occurred.
The previous user-confirmed physical dashboard return remains historical evidence
for the closed inventory ticket and does not validate these new candidates.

Evidence and continuation:

- [Final lifecycle result](lifecycle004/REPORT.md), with retained failed predecessors
  [001](lifecycle001/REPORT.md), [002](lifecycle002/REPORT.md), [003](lifecycle003/REPORT.md).
- [HAL build and limits](handoff001/REPORT.md) and [ownership contract](handoff001/CONTRACT.md).
- handoff-lifecycle-review001.json verifies source/artifact hashes, failed-build
  snapshots,52 Python sources, scoped cold integrity and all four closed journals.

All PCI builds, guests and cold readers are closed. No PCI resource lease remains.
The next runtime gate requires supported completion of pending setup, followed by
a fresh normal restart/persistence test. HAL native validation and shared-client
integration remain separate work before any physical deployment.
