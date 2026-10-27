# Continue from the closed component review700

Do not rerun the608 linked encoder fixtures,256 GPU fixtures, or physical699.
Read REPORT.md, sources001.json, both build records and both fixture records.

The next native experiment must resolve the remaining GPU initial-state contract
before writing the encoder. Prepare a narrowly scoped read-only capture of GPU
PCI identity/memory decode/BAR, pixel-clock/selection registers, PCRTC config and
start, output control, and CRTC format/stride/interlace. Validate exact readable
addresses and indexed-register selector restoration against the pinned sources.
Capture pre-transfer kernel context separately from post-transfer native values.
Use the checked owned-page handoff, fresh source/binary pins and full-transition
host fixtures. Do not use measured firmware values as programming tables.

If that review establishes an adequate precondition, implement the complete
blank/setup/encoder/verify/enable transaction with a distinct owned pattern
framebuffer contract. Do not link700's55MiB Windows reservation onto the current
kernel-owned framebuffer. No legacy interrupt-status clearing, NVSetFBStart
helper, speculative memory-controller write or unbounded wait may be imported.

Only after linked failure-path tests and exact staged readback should a watched
native480p pattern run. Windows1.6 follows visible pattern qualification; kernel
mode success alone is insufficient. No physical launch is staged by700.
