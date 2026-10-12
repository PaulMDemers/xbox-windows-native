#274: terminal owner capture implemented and compiled; never launched

The exact273 renderer now has a separate one-shot terminal capture. finish274
publishes new metadata under FIFO synchronization; the actual PFIFO worker
performs the final CPU/context checks, captures a second immutable ownership
graph, and seals the273 lifetime observer. The original265 graph is retained.
No texture reference is released, no existing actor is reset and no guest or
physical console was accessed.

Host001 tests the actual admission and native-context matching functions with
ASan/UBSan:262938 cases pass. Host002 extracts the actual end-worker body from
compiled build001 and exercises24 success/failure paths using explicit CPU,
GL, graph and lock models. It verifies balanced locks, unchanged initial graph,
failure quarantine, no rearm and no repeated work. These models do not execute
actual CPU-exclusive jobs or GL fences; runtime confirmation is still required.

Build001 compiled successfully but did not report CPU acknowledgment identities
when the callback count was zero. It is preserved and never launched. Build002
adds CPU thread IDs, epochs, timestamps and the deadline to the report. The
worker/admission/context bodies are unchanged; source review must establish
that equivalence before carrying the host tests forward. Neither build is a
live completion, texture reuse, retirement or acceleration result.

Reviewed build002 is private at
E:/Codex-archive/xbox-windows-native/boundary274-build002/xemu-boundary274.exe,
191771501 bytes, SHA256
3c3c61fff0615a2e2781b90a3f4ed9a6b119e343222e5defdcad4f0ea4cd806e.
Both builds have79 inherited warning instances and no new warning messages.
Review rehashed42 private source files across the two builds, six frozen build
inputs and12 host-test files. Build002 differs from001 only in the report
formatter; all tested transaction functions remain identical. All owned
processes are closed, including builds26501/52041.

The change uses three files on the exact273 source closure:renderer.c, its header
and a read-only observer-ready predicate in texture.c. It retains the original
normal binder/destructor,273 accounting and273 terminal format. Borrowed source
restoration, executable hashes and inherited warning comparisons are recorded
in the build and final reviews. No shared SDK objects or native drivers changed.

An initial PowerShell inline generator failed parsing before source generation;
prepare-source.py replaced that transport. A patch application failed its exact
anchor check before any edit; the corrected patch used the actual source lines.
No guest launch, test result or existing frozen build was overwritten by either
host authoring failure.

Next is the explicit standalone controller and independent paired-graph,
terminal and texture-snapshot qualification. The full15 RAMHT descriptor proof
is still required. Do not reuse the Windows258 attestor as a substitute. Keep
272's strict reserved-sector disk failure,269's observation overflow and every
historical failure distinct. The physical audio-integrated demo is unchanged.
