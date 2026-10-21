#633 native480p candidate built; initialization checked, Windows pending

The separate loader builds for720x48032bit with the existing64MiB/55MiB/9MiB
reservation. Mode3 uses632's newly verified programming facts. Existing720p and
1080i profile values remain identical. The adapter accepts only Conexant/HDTV
with the corresponding enabled progressive flag; explicit480p refuses legacy
fallback on unsupported hardware. Bounded19-write sequencing, timeout handling,
geometry/pitch/format readback and fail-blank behavior are retained. No clock or
PCRTC values are borrowed from observations. Default boot selection remains720p.

The fresh source tree builds with pinnedGCC12. Pure profile tests pass129 checks;
modeled transaction tests pass235552 assertions across720p/480p success, each
SMBus failure, busy/timeout, sync/vblank stalls and readback/configuration faults.
ASan/UBSan pass. The compiled profile exactly matches632; old profiles exactly
match310. The layout, loader path, mode3 argument and inherited warnings were
reviewed. Candidate XBE is private C:/xwn633/build001/default.xbe, SHA256
`a53a09427f80411efee73ef53da0ec9829f8af0d27d404f5a3ff818e96b4bde4`.

Fresh emulator004 reached the actual wrapper return with result1, exact compiled
text, state(stage5,error0,19/19 completed writes),720x480 handoff dimensions,
framebuffer03700000 and32bit format83. Timing values match stock631 on the same
pinned emulator. Full physical timing equality is NOT established: several
registers return0 in this emulator, as also observed in stock631. A local primary
source reference omits those registers, but correspondence of that source to the
binary is not proven. The matched actual control is the basis of the scoped test.
This stopped before Windows; no desktop, drawing, normal shutdown or physical
native-mode qualification follows from it.

Failures retained:001 observer exceeded the protocol's131072-byte read limit;
002 preparation changed a historical pin path and never launched;003 compared
against physical timing and failed on emulator zeros.004 initially hit the
projected-space guard before launch, then ran after reclaiming three redundant
closed xemu executable copies (66,776,340 bytes) with two exact recovery paths.
No disk, firmware, capture, source or backing chain was deleted or moved. Every
actual emulator run failed strict disk equality on the known reserved-sector
byte; filesystem bytes inherited unchanged. These failures remain failures.

All633 attempts are CLOSED; no owned process or breakpoint remains. Never rerun,
recollect or parent the closed runtimes. The633 candidate was not installed or
launched on the console. Original720p launcher/startup/package remain unchanged.
No live Windows resolution selection, other-revision or acceleration claim.
