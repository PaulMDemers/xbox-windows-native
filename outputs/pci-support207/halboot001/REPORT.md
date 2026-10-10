# Native HAL control and candidate boot validation

Later cancellation coverage is recorded in [cancel001](../cancel001/REPORT.md):
genuine QUERY_REMOVE/CANCEL_REMOVE and recovery passed. STOP/CANCEL_STOP and the
remaining functional/shutdown gates below remain unqualified.

Both the rebuilt control and shared-ownership HAL candidate booted NT5 in fresh
owned emulator fixtures and passed the resource-only lifecycle workload. The
candidate's new XwnSmbusReadV1 export was called successfully four times, including
after removal and re-enumeration. Every call used the fixed invalid addressFF /
commandFF and returned INVALID1 with NTSTATUS0, status0, polls0 and data0. The
control consistently reported the export absent. No functional SMBus transaction
was requested.

| Variant | Launch UTC | Closed UTC | Export present |
|---|---|---|---|
| control | 2026-10-10T20:39:31.619715+00:00 | 2026-10-10T20:42:32.082484+00:00 | 0 |
| candidate | 2026-10-10T20:44:29.282706+00:00 | 2026-10-10T20:47:29.934063+00:00 | 1 |

Each run completed real installation/start, DICS_PROPCHANGE, six D3/D0 power
transitions and safe removal/re-enumeration. The trace records two QUERY_REMOVE /
REMOVE pairs and three START sequences. Four successful native API probes bracket
those operations. The driver still rejects ordinary telemetry. STOP and cancel
paths were not observed and remain unqualified.

Both runs reached the normal-restart guard and held on pending installation258.
No restart was requested, no EventLog6006 or dashboard return occurred, and both
closed at their180-second host bound. These are diagnostic boot/lifecycle results,
not normal-shutdown or two-boot persistence qualification. The appended SetupAPI
history names APU01B0; audio's report continues to identify that device as
unsupported. No setup dialog was dismissed and no device was disabled.

Cold audits passed protected files, five structural hives, retained SetupAPI/event
history, complete F: allocation and the new E: allocation audit. E: has19 directories,
43 files and380 owned clusters after the larger HAL replacement, with no orphans
or crosslinks; its allocation metadata is unchanged across each guest run. Full
configuration equality is not claimed. Inherited Ftdisk49 remains a strict
whole-boot failure; all new events are retained in each audit.

The same build001 driver/helper/INF is used for both variants. Prepared protected
file differences are exactly the HAL and startup's expected-export flag.
The control HAL SHA256 is77333f86600d320687baf61a562ab718c7974ef24d3d614211b87bd971890ade;
the candidate is234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255.
The parent handoff001 manifest retains exact source trees, ordered patch series,
compiler flags, imports and exports. This closes its previously untested native
boot/invalid-ABI gate, while preserving the distinction between rebuilt control
and installed baseline bytes.

Preparation001 failed before any guest launch because its no-growth condition
rejected the larger HAL. Its partial private control001 fixture and failure
journal remain preserved and must not be launched. Attempt002 uses fresh images
with complete E: allocation audits before and after replacement. Eleven explicit
valid/corruption cases test that audit. Resource-policy5,751 sanitizer cases and
the actual NT5 import/no-port-I/O review pass for the helper package. Comparison001
verifies unchanged build/attempt source pins, artifact hashes, matched fixture
scope, all native probe replies and the closed cold-audited results.

All owned guests, cold readers and resource leases are closed. No physical-console
connection, deployment or ticket reuse occurred. Terminal takeover, stuck-bus
runtime behavior and allowed SMBus reads were not exercised. Keep functional
telemetry disabled. Next gates are supported resolution of pending setup followed
by normal restart/persistence, STOP/cancel coverage and coordinated functional
client/terminal validation. Hardware readiness remains false.

Evidence: [procedure](PROCEDURE.md), [comparison](comparison001.json),
[control](control002/pnp-review.json), [candidate](candidate002/pnp-review.json),
[control cold audit](control002/audit.json), [candidate cold audit](candidate002/audit.json),
[preparation failure](preparation001-failure.json), [E: audit tests](e-tests001.json).
