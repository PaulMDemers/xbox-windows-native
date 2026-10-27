#718 CLOSED: optical evidence identifies failed CR1b restoration

The photo decoded all416 bits with threshold/offset checks and352 middle bits
with independent adjacent-row geometry. Native CR1b saved85 -> target05/readback05;
one restore85 attempt read back05. Bridge returned7184, payload phase5/error7184;
wait not entered. The cause of bit7 not returning remains unknown. The panel
cannot separately establish finalSEQ1/context checks. No717 exact-error inference
or708/709 full-mode cause claim; no sustained05 or Windows1.6 qualification.

Manual power-cycle Ready; nine preparation files collected ONCE and audited.
Source/binary/report/photo pins and independent alias checks pass. PCI/CRTC/SEQ,
geometry and allocation words match716/717. Preparation PASS is not native PASS.
No reset or new launch pending. Console dashboard, no hook/owned host process;
build/xemu released, hardware ticket retained; original720p protected, other work
and automation tabled. All718 and earlier runtime attempts CLOSED.

Next: source/read-only review of CR1b bit7 restoration before a fresh diagnostic.
Do not mask bit7, write CR22 or repeat full-mode setup blindly. A future test must
measure its own post-reset baseline; this collection contains pre-test readings.
Read718/REPORT.md, observation001.json, audit001.json and NEXT.md.
