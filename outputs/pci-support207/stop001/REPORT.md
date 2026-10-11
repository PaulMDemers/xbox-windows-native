# Native STOP and CANCEL_STOP recovery demonstrated

One fresh NT5 emulator boot demonstrated genuine OS-generated STOP/START and
QUERY_STOP/CANCEL_STOP recovery for the resource-only SMBus DEV_01B4 driver.
This was an explicit diagnostic rebalance requested through
IoInvalidateDeviceState, not an ordinary-boot observation or a functional
SMBus transaction. The HAL ownership candidate stayed unchanged at
234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255.

The allow phase produced QUERY_STOP, STOP and START. Its counters reached one
STOP and two STARTs, with the device started, powered and accepting queries.
The veto phase returned STATUS_UNSUCCESSFUL for the next QUERY_STOP and Windows
sent CANCEL_STOP. STOP and START counters remained one and two, and a fresh
interface query succeeded. Both one-shot flags were consumed and cleanup
reported successful disarming.

The full trace contains two QUERY_STOP events, one STOP, one CANCEL_STOP, four
STARTs, three QUERY_REMOVEs, one CANCEL_REMOVE and two REMOVEs. Its 61 records
form three contiguous driver-load segments of 13, 36 and 12 records; none reaches
the 64-record cap. All four raw/translated START resource lists are identical
52-byte lists. The port remains C000 with the existing constrained resource policy.

The subsequent held-handle removal veto returned CR_REMOVE_VETOED 23 and
PNP_VetoOutstandingOpen 5 for the exact device. Its retained handle recovered,
STARTs stayed at two, and the query counter advanced from one to two. After the
handle closed, safe removal, interface disappearance and re-enumeration passed.
Seven native invalid-only HAL ABI probes and six D3/D0 transitions passed.
Ordinary telemetry remains disabled.

The guest launched at 2026-10-10 23:06:46 UTC and was closed by the host at
23:09:46 UTC. Normal Windows restart was held by pending installation 258;
the helper exited 33 and new SetupAPI history identifies unsupported APU 01B0.
There was no restart request, EventLog 6006 or dashboard return. No unrelated
setup dialog was dismissed. Host-bound closure does not qualify normal shutdown.

Cold protected-file, five-hive, old-log-history and complete E:/F: allocation
checks passed. E: allocation metadata stayed equal to the prepared fixture.
F: contains 319 directories and 6,726 files, with zero allocation errors or
orphan clusters. This establishes cold integrity for this fresh run, not
repeated-boot storage safety or coverage of the separate USB second-boot issue.

Whole-boot qualification remains false. Besides the recurring Ftdisk 49 error,
this run logged two Mouclass 9 errors, two Kbdclass 9 errors and one DHCP 1005
warning. These were absent from the preceding cancel001 trial's new warning/error
set. Their cause is not established. The resource-rebalance intervention can
involve other device stacks; target recovery alone does not qualify their behavior.
The full typed binding delta and event records are preserved for follow-up.

Installed driver SHA256:
3c906ae0cb7cb7af794de7caeabb99e52d15e00b8bc10135f8e28a8632ce1a92.
Installed OEM-INF SHA256:
d8b50e1f6e49c7a3d1a0aea3a4fee0219351c9be8b7f8121ab02ab47d8c53e83.

Build 001 failed before guest preparation on three unannotated intentional
fallthroughs and is frozen in failed-build001. Build 002 adds only the required
fallthrough comments to that driver source. Compiler/source/artifact pins,
actual NT5 imports, absence of direct port I/O and 5,751 sanitizer-backed resource
validation cases passed. The cold E: checker is unchanged from the tested version.

All PCI build, emulator and cold-reader sessions are closed. The used fixture
must not be relaunched. No physical access, closed-ticket reuse, root-fixture
integration or other-owner driver changes occurred. Functional reads, terminal
takeover, normal restart, repeated-boot persistence and physical readiness remain
open. The extra input/network events need investigation before broader qualification.

Evidence: [procedure](PROCEDURE.md), [build/import review](build-review002.json),
[runtime review](review001.json), [trace review](trace-review001.json),
[actual IRP trace](candidate001/resource-trace.json),
[cold audit](candidate001/audit.json), [run closure](candidate001/run.json),
[pipeline stages](pipeline002.json).
