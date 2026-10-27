#725 CLOSED: firstCR1b85 sample follows680630 restoration

One accepted SITE launch2026-10-27T17:45:19.850012+00:00. User observed orange
holding and supplied full13row photo. Top green visible. Independent component
and multi-threshold/offset sampling plus adjacent-row interpolation passed.
No expected register values were used to choose bits; signature validated last.

Decoded rows:
7250000d,4,5,7255,11,4,05,05,85,85,85,85,0.

| CR1b sample | Value |
| --- | --- |
| Existing immediate read after05 write |05|
| AfterCR19 restore |05|
| After680630 restore2to3 |85|
| After output gate4 |85|
| AfterSEQ1 restore/readback |85|
| Existing final cleanup read |85|

Forward11MMIO+4CRTC checks completed; native result7255 is cleanup failure.
The first observed bit7 change lies between the post-CR19 sample and the
post-680630-restoration sample. This brackets an observation, not causality or
register semantics. Four added reads change timing. Other cleanup fields are
not exported, so additional cleanup mismatches remain unknown.

The data-write sequence is unchanged from724; noCR22 data write,85 restore,
repeatCR1b write, pending-bit clear, mask waiver or encoder/timing programming.
This does not qualify native1.6 mode switching, Windows or acceleration.

## Collection and failures

User power-cycled after photo. collection001 connection was refused before
any file was read and before its private collection directory was created.
Preserved failure; new transport attempt002 collected the nine reports once,
with matching double-read. No relaunch or closed-runtime recollection.

Initial local audit001 mistakenly referenced closed724 collection002 (which
does not exist); preserve that local audit failure. Fresh audit002 corrected
the reference to retained724 collection001, without any network connection.
It passed source/build/stage pins, allocation/alias bounds and private photo
pins. PCI/CRTC/sequencer/geometry/allocation-plan preparation exactly matches724.

Last durable phase handoff_armed. Pre-arm CPU286/8001003b/f000/610 is kernel
preparation, not final/native context. Native values come from photo001 only.
Console is now at UnleashX. No startup hook, owned host process or VM. Manual
power cycle is not a normal Windows shutdown. Runtime725 is CLOSED.

Also preserve host001 stale16-entry relocation assertion; fresh host002 exact17
passed. Private photo/binaries/firmware/credentials are not published. All
failure receipts and frozen source remain unchanged.
