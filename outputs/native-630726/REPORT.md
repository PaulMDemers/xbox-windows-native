#726 closed:630-only control retains CR1b85

One launch was accepted at2026-10-27T18:13:46.296106+00:00. The user observed
a green held picture. Private photo001 was decoded from isolated components,
with five sample offsets, three thresholds and adjacent-row interpolation.
All416 bits agree; expected register values were not used to select the bits.

| Stage |630|CR1b|
|---|---|---|
|Baseline|3|85|
|After blanking|3|85|
|After write2|2|85|
|After saved3 restoration|3|85|
|After output restoration|3|85|
|Last of32 late pairs|3|85|

Raw13 rows:7260000d,4,5,726,2,30085,30085,20085,30085,30085,30085,0,22007.
Return726, two630 writes, zero lateCR1b changes, final cleanup and selectors pass.
CR1b was never written in this control. Samples are sequential, not atomic;
late intermediate values/min/max remain unexported. The previous05->85 change
was not reproduced by630-only writes. Interaction with explicitCR1b writes,
other setup operations or timing is unresolved. No bit7 mask or driver fix follows.

After user-confirmed power cycle, nine preparation reports were collected once
with matching double-read. Source/build/stage/photo pins, framebuffer and alias
bounds, and unrelated E-root/application entries passed audit001. PCI,CRTC,
sequencer,geometry and allocation-plan preparation exactly match closed725.
The final persisted phase is handoff_armed. Pre-arm CPU286/8001003b/f000/610 is
kernel preparation, not final/native context. Native values come from the photo.

Collection/audit passed on their first attempts. Preserve integration001's
incorrect harness expectation for aCR19 low-bit mutation; fresh integration002
corrected that expectation without changing the diagnostic binary. Also retain
all prior failures. This run qualifies only this bounded control, not full
mode switching, Windows1.6 or GPU acceleration.

Console is now UnleashX. Manual power cycle is not normal Windows shutdown.
No startup hook or owned process/VM remains. Runtime726 CLOSED; no repeat launch,
recollection or parenting. See NEXT.md for the minimal interaction test design.
