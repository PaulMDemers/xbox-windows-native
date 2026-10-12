#273: bounded lifetime observer compiled; no guest launched

The exact269 observer now records repetitive callbacks as exact counted runs,
while reserving each of four generations' first bind and final free. This removes
the known per-decrement file bottleneck without discarding events or relaxing
the saturation gate. No268 release helper is installed. No native, SDK or
physical driver changed, and no273 guest was prepared or launched.

Renderer build001 is private at
E:/Codex-archive/xbox-windows-native/lifetime273-build001/xemu-lifetime273.exe:
191760677 bytes, SHA256
be818c61fd5b8641335472d32f680a215a8b8197ed706dd3e31b326f0a976102.
Only texture.c differs from exact269 build005. Replacing the diagnostic block
with its predecessor reconstructs the original texture source exactly. All19
borrowed source files were restored. The79 compiler warnings have inherited
messages; no new warning message appeared. This is compilation evidence, not
an emulator or GL result.

Host002 compiled the actual extracted gate, callback, seal and serialization
functions with ASan/UBSan. One million repeated decrements, four modeled bind
snapshots, tombstones and4096 publication/seal races passed. An independent
little-endian decoder reconstructed1000006 events from two runs plus reserved
records and rejected115 semantic/truncation mutations. Snapshot, file-open,
write/close, busy, foreign-owner and closed-gate failure paths were exercised.
GL capture and file-open interfaces are modeled in this harness; actual GL
state restoration remains a runtime requirement.

Host004 forced128-run saturation, then captured all four reserved first-bind
and final-free records. Every one of8960 undersized output capacities refused
without modifying the output buffer. The serialized failure retained the
nonzero core error and the independent decoder rejected it. Diagnostic records
surviving overflow do not turn incomplete observations into a PASS.

Host001 failed compilation on misleading indentation in the harness. Host003
failed compilation after a renamed prior main function lacked a return. Their
private capsules and original results remain preserved; neither was executed.
Host002 and004 are distinct corrected attempts, not replacements of failures.

Source review also identified a remaining completion boundary: inherited
seal269 closes the observer gate on the monitor thread, but does not request a
new PFIFO/context/CPU acknowledgment after guest reuse. Initial265 capture has
such acknowledgments. A sealed terminal file alone cannot establish completion
of resumed graphics work. DESIGN.md and NEXT.md require a separate fresh actor
before full control qualification; no existing one-shot actor will be reset.

All owned processes are closed, including build71621. No runtime pixel,
four-generation reuse, disposal, speedup, Windows GPU ownership or physical
qualification follows from273.272's independent pixel control remains scoped
PASS with strict disk equality FALSE for its reserved-sector byte;269's old
overflow failure remains failed. All other historical failure gates remain.

Closed265/266 non-backing portable files were hash-verified onE and retained via
original-path junctions under portable-273.json. No backing disk was moved.
The20GiB build/projected-launch guard remains unchanged.
