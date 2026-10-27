#727 closed: minimal CR1b/630 interaction reproduces05->85

Single launch accepted2026-10-27T18:47:11.077080+00:00. User reported green;
the photo shows an intact held report. Independent cell components, five sample
offsets, three thresholds and adjacent-row interpolation agree on all416 bits.
No expected register values selected the bits; signature checked afterward.

| Stage |630|CR1b|
|---|---|---|
|Baseline|3|85|
|After unlock, before CR1b write|2|85|
|Direct read immediately after one05 write|2 (last sampled)|05|
|Read after reselecting CR1b|2 (last sampled)|05|
|After saved6303 restoration|3|85|
|After output restoration|3|85|
|Last of32 late pairs|3|85|

Raw13 rows:7270000d,4,5,727,10102,30085,20085,50005,30085,30085,30085,0,1022007.
Return727, two630 writes, oneunlock, oneCR1b write, zero late changes, cleanup
and selector checks pass. There is no repeatedCR1b write or repair operation.

The reduced sequence reproduces725's observed05->85 change without its other
prefix writes.726's630-only control retained85. This supports investigating
the interaction; it does not prove bit7 semantics, strict write causality,
cache effects or the root cause of full-mode708/709 black screens. Samples
are sequential; read traffic and timing differ from the larger prefix.

After user-confirmed manual power cycle, nine preparation records were collected
once with matching double-read. Audit001 passed frozen sources/binaries/staging,
private photo pins, independent framebuffer/alias bounds and unrelated E entries.
PCI/CRTC/sequencer/geometry/allocation-plan preparation exactly matches726.
Last persisted phase is handoff_armed. Kernel pre-arm286/8001003b/f000/610 is
not the final/native CPU context; native results come from the photo only.

No727 build, test, collection or audit failure. Earlier failed evidence remains.
Console UnleashX; no hook/owned host process/VM. Manual reset is not normal
Windows shutdown. Runtime727 CLOSED. No full-mode/Windows1.6 or acceleration
qualification. See NEXT.md for a matched kernel-context comparator.
