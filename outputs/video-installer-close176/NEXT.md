All owned173–176 sessions CLOSED. Never relaunch or recollect these cases.

Read REPORT.md, candidate001/token-race-verification.json and evidence-review.json.
The token1880 supplied to an01B4 installer in services.exe is successfully closed
by another thread in the same owner EPROCESS between a successful query and the
later C0000008 query/outer error6. Immediate wrapper kernel32!CloseHandle pinned;
higher closing-thread caller and exact ownership protocol remain unknown.

Next unique bounded child should capture the actual closing-thread caller chain
with resident-byte/module identities and proper frame interpretation, and pair
the owner's acquire/publish/clear/close lifecycle with the installer call. Do not
use a guessed EBP chain or static source symbol as runtime attribution. Capture
unknown/nonresident frames honestly. No speculative token duplication patch,
forced success, service/event/PnP suppression, UI automation or gate waiver.

Shutdown popup is a separate producer:174 had one despite no hard-error API hit;
175/176 had an invalid-token installer failure with no popup. Retain both results.
StrictFALSE sole exactFt49 in175/176; full cold workload/integrity/normalshutdown
passed. Debugger timing is not ordinary qualification or a physical finding.

Before new preparation inspect capacity/closed-artifact manifests: C free
21690884096 bytes, unchanged20GiB guard. Offload only verified closed standalone
chains with hash/readback and explicit source paths; no casual backing moves.
Physical0101/video0093/0088rollback/immutable0.1.0 unchanged; no physical test is
qualified by these emulator diagnostics. Final176 source differs from initial
api-scope-review source; initial snapshots and final002 tests are both preserved.
