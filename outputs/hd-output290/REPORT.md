# Standalone720p/1080i and low-resolution return passed

The corrected controller removes the hardware checkpoint, executes exactly the
original first4-byte instruction, verifies EIP and reinstalls before continuing.
One fresh unused blank8GiB child used the SAME289 native XBE/private HD fixture.
No guest memory/register edits, new native build or physical access. The copied
preparation script's informational line still says289; actual roots, runtime
records and unique task identity are290. No prior runtime was reused as a parent.

Actual phases11/22/33/44 completed. Full framebuffer bytes independently match:
720p1280x720:3,686,400;1080i API1920x1080:8,294,400;fallback640x480:1,228,800.
Total13,209,600. Every framebuffer page was translated from the actual CR3/CR4;
reported physical allocation equals scanout; first/last virtual pages agree with
physical readback. Actual loaded XBE header/sections/full text/checkpoint/callers
are pinned. Timing registers were retained, not turned into an unreviewed mode
programming recipe. Of note: fallback640x480 reports HVALID719, so visible timing
width must not be blindly substituted for framebuffer pitch.

This is a standalone stock Xbox kernel API and framebuffer-memory result. It is
NOT physical1080i signal/field/monitor validation, Windows boot handoff, performance
or GPU ownership qualification. The physical console remains on its tested
FATX0101/display118/shared158/audio004 baseline and standard-AV HDMI adapter.

Breakpoint/physical-mode cleanup passed, terminal44 was observed, then a12-second
resume window and orderly host exit0 with no fallback kill. Actual firmware reboot
entry was not traced. All frozen sources/dependencies and private captures rehashed.
Both QCOW structures and private EEPROM unchanged/clean. Strict full-disk gate
remains FALSE: one reserved-sector byte; full8GiB mapping plus65,536 overlay bytes
prove filesystem bytes inherited unchanged. The possible power-count interpretation
is not writer attribution and does not waive the original gate.

No shared SDK/source changes, Windows/physical deployment or0.2.0 tag. Automation
remains paused. Never relaunch, recollect or parent this closed runtime.
