# Bounded HAL SMBus ownership candidate

The experimental HAL candidate compiles and passes 65,894 ASan/UBSan core-model
cases, including fatal takeover at 16 callback boundaries. Existing HAL export
ordinals are preserved; all 84 imports resolve against the pinned NT5 providers.
Linked-code inspection confirms CLI precedes terminal calls/I/O and the shared
owner, terminal result and public entry live in non-discardable sections.

Candidate SHA256: 234b1714debe84ede144b9b1717cf46d2639f3c31b63669c120d7c777a2a6255.
It has not been booted or deployed. Resource-only guest trials use the installed
baseline HAL. This is compiled/model/static evidence, not native broker execution
or physical qualification. Functional telemetry remains disabled.

## Implementation

broker.h owns the controller in the HAL's lifetime, rather than in a removable
function driver. Claims are atomic and nonblocking. Only the three existing
passive telemetry requests are accepted. Completion timeout quarantines further
clients until reboot; driver reload cannot clear that quarantine.

The terminal path disables interrupts on the free UP target, permanently takes
ownership, waits boundedly for idle, then issues at most one SMC power command.
An interrupted client cannot resume because the wrapper never returns or restores
interrupts. No driver-held lock is awaited. Idle and completion each permit at most
10,000 polls, with 10-microsecond stalls. A controller that never becomes idle
causes a terminal halt without another command. This removes unbounded polling;
it does not guarantee recovery to the dashboard from a stuck physical controller.

No abort strobe is assumed safe on hardware. Future functional clients must use
XwnSmbusReadV1, retain PnP/remove/power ownership and pin the resources first.
The old raw-I/O prototype is not a coordinated client. CONTRACT.md documents the
four-ULONG reply ABI, UP/noreturn assumptions and remaining driver/lifecycle gates.

## Reconstruction and limits

Build001 replayed the pinned ordered0088 series from base
afc0127e8f937ab68503d715d948844973756aa1 into a fresh E: source tree, verified
adf9b3d166ef84630a48d7393fcc9fe3ce78f104, and used the pinned RosBE2.2.1/GCC8.4.0
boot-profile flags. The new patch produces tree
24cea3bc33dd7f6fb34f2ff50d7ebdec2f9ff1fb. Shared WSL source remains untouched.
The build ran from19:36:08 to19:55:49UTC, mostly source checkout, clean-tree checks
and CMake generation on the Windows volume. Cooperative lease contention is
preserved separately. The build and its lease are closed.

The fresh baseline SHA77333f86600d320687baf61a562ab718c7974ef24d3d614211b87bd971890ade
is not byte-identical to installed HAL
a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648.
The images retain identical text/data sizes and relocation offsets. Longer
embedded source paths expand rdata and shift later sections by a page. The seven
non-relocation text-byte differences are relative calls into that moved INIT
section; sampled INIT differences likewise reflect relative call displacement.
baseline-comparison001.json and baseline-instructions001.json retain the actual
differences. This explanation is not an assertion of complete image equivalence.
A control/candidate native boot rehearsal remains required before promotion.

## Evidence

- build001.json, tests001.json and host-compiler001.txt: commands, source/tool pins,
  model cases, artifact hash and times.
- 0001-hal-shared-smbus.patch: exact candidate change against the reconstructed tree.
- build-review001.json: actual NT5 imports, export compatibility, PE architecture
  and installed/rebuilt baseline comparison.
- linked-review001.json: resident symbols and actual terminal/ABI disassembly.
- CONTRACT.md: allowed clients, gate semantics, finite polling and failure behavior.

No physical-console connection, ticket, deployment or telemetry operation was made.
The closed hardware220 ticket remains closed. Native lifecycle/restart success,
future client integration and physical controller behavior remain qualification
requirements; inherited Ftdisk49 is not waived.
