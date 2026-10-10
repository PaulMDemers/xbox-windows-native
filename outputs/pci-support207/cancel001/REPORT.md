# Native query-remove cancellation passes

One fresh NT5 emulator boot demonstrated a genuine query-remove cancellation for
the exact SMBus01B4 device. Windows returned CR_REMOVE_VETOED23 with
PNP_VetoOutstandingOpen5 and named that exact PCI instance. The driver trace
contains QUERY_REMOVE(1) immediately followed by CANCEL_REMOVE(3). The original
held interface handle then completed its query successfully: starts stayed1,
while the query counter increased from0 to1. Recovery did not require restarting
or re-enumerating the device.

After closing the held handle, a fresh interface query succeeded. Ordinary safe
removal then succeeded, the interface disappeared, and re-enumeration restored it.
The full run contains three QUERY_REMOVE events, one CANCEL_REMOVE, two REMOVE
events and three START sequences. Five native invalid-only HAL probes and all
six D3/D0 transitions passed. Ordinary telemetry remains disabled. The HAL is the
unchanged, previously boot-tested ownership candidate234b1714…a6255.

The guest launched2026-10-10T22:22:26UTC and closed22:25:26UTC at its180-second
host bound. Normal restart was held on pending installation258; the new SetupAPI
history again names unsupported APU01B0. No restart request, event6006 or dashboard
return occurred. The intentional removal-veto result is successful cancellation
test evidence; the separate pending-install refusal remains a failed shutdown
qualification gate. No unrelated setup dialog was dismissed or device disabled.

Cold protected-file, five-hive, old-log-history and complete E:/F: allocation checks
passed. E: allocation metadata matches the prepared fixture. The only new logged
error remains inherited Ftdisk49; strict whole-boot success is false. This single
fresh boot does not establish repeated-boot storage safety or cover the separately
reported USB second-boot failure. The fixture is closed and must not be relaunched.

Installed driver SHA256:
0cf41ac07f2197282e78c4c46c612deb65b42aecbea57c759802211791af6837.
Installed OEM-INF SHA256:
0bcab472c86fb58d4fb69f4c8465303ab5406d7a0af693d4569f5ed0f37dc9ab.
Build/source/artifact hashes match; actual NT5 imports and no-port-I/O checks pass.
The existing resource-policy suite passes5,751 sanitizer cases. The E: checker is
byte-identical to the previously tested implementation. review001.json verifies
the exact veto, trace counts, retained-handle counters, post-close recovery, native
API results and cold closure.

STOP and CANCEL_STOP were not observed. Supported DICS_PROPCHANGE produces
removal/recreation here; documented API guidance discourages DICS_STOP/START, so
those calls were not substituted to manufacture STOP coverage. Functional SMBus
reads, terminal takeover, normal restart/persistence and physical readiness remain
open gates. No physical connection, ticket reuse, root fixture integration or
other-owner driver integration occurred. All PCI guest/build/cold-reader leases
are closed.

Evidence: [test procedure and API references](PROCEDURE.md),
[review](review001.json), [PnP log](candidate001/pnp-review.json),
[actual IRP trace](candidate001/resource-trace.json),
[cold audit](candidate001/audit.json), [closure](candidate001/run.json).
