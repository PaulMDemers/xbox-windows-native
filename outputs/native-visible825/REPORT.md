# Native825: first visible complete native Xcalibur mode transition

Test824 completed the same corrected transaction in Xbox-kernel context and
returned automatically. Test825 subsequently left that context, changed the
initial blue picture to the green low-resolution picture, and held it, as directly
reported by the user. This is the first visible complete native transition in this
sequence. It is not a Windows boot or native720p qualification.

After explicit power off/on, FTP independently authenticated UnleashX. Nine
preparation records were collected once; the local audit verified frozen sources,
private binaries, report hashes, allocation/alias separation and handoff_armed.
The native result structure was not persisted. Do not turn kernel preparation
fields into claims about native transfer counts or pixel-readback counters.
Border/checkerboard were included in the question but not separately described.
All owned host CPU fixtures are closed. No startup hook was installed.

## Windows integration boundary

The existing NT5 miniport reads retained scanout geometry and pitch and exposes
one framebuffer mode. FreeLoader also reads this layout and requires the HD
reservation when built with that profile. The immediate implementation target is
therefore Xromwell's mode initialization and loader handoff, followed by an actual
Windows boot; a new Windows mode-switching driver is not the first step.

The qualified probe uses an nxdk-owned framebuffer and identity-mapped native
pointer. Xromwell instead reserves physical03700000 through04000000 (9MiB) and
uses FB_START=f3700000. Do not copy the probe address or fabricate its ownership
checks. A fresh adapter must validate this reservation, access aliases, CPU state,
actual starting geometry and native chip/cable/timer admission independently.
Keep the exact tested CR19 address calculation and PAS0 palette ownership fix.

The ordinary Xromwell BootVgaInitializationKernelNG writes PCRTC_START before
its existing HD hook, and its legacy path later writes CR1b/CR22/CR33. Insert a
separately gated Xcalibur path before these mutations; do not fall through to
legacy setup after partial initialization. Review BootResetAction's earlier
EEPROM/bus calls and assembly entry, since failed689 did not establish their
native behavior. Preserve the original Conexant720p path and source manifest.

Next: fresh source-only launcher candidate from the pinned reconstruction tree,
with separate full-image host tests for mapping, reservation, entry/admission,
refusal, final geometry and continuation into FreeLoader. No new launch is admitted
by this note. Windows desktop requires the later watched boot, mouse/text checks,
persistence and normal restart. CLOSED825 must not be rerun or recollected.
