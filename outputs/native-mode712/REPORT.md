#712: bounded blank-and-restore pair at unchanged720p

711 visibly returned the native baseline-only checkpoint before blanking.712
retains that baseline and the32KiB bridge/ownership contract, then tests only the
first display-blanking operation and restoration. No encoder, geometry, timing,
clock, interrupt pending/enable or framebuffer-address programming is added.
The ordinary Windows720p launcher remains protected.

## Native sequence

Require exact native sequencer1=1 in addition to the previous baseline checks.
Save the indexed selectors. Set sequencer1 to0x21, request byte80d3=5 and read back
the exact sequencer value. If accepted, wait a nominal3375000 ticks at the kernel
3375000Hz rate, with at most1000000 additional reads. Reject backward/large steps,
24-bit wrap or excessive elapsed time; accept uint32 rollover. This is not an
independent clock calibration. Native timer prerequisite699 had observed progress.

After the blank request, every ordinary return path attempts exactly ONE restore:
byte80d3=4, then the exact admitted sequencer1=1. Check sequencer/context readback
and restore index selectors. No retry or subsequent reblank. This diagnostic
recovery pair differs deliberately from704's post-programming failure policy:
712 has made no encoder/geometry changes to recover from.

The disable/enable requests and their provenance are pinned in source-review001.
ACPI has no independent readback. The model includes dropped gate requests that
software cannot detect. A green bar alone therefore proves only software checks;
the user's observed disappearance/restoration is separate physical evidence.
If black persists, exact native phase remains unknown; preserve it and manually
reset after observation. No LED/UDP fallback or implicit success is assumed.

Results:0x712=sequence checks complete;0x7121=initial sequencer rejection;
0x7122=blank sequencer readback failure;0x7123=timer failure;0x7124=restoration
readback/context failure. The176-byte result stores saved/blank/restored sequencer
values and wait status in the existing256-byte owned result slot. All prior
argument/layout/IF/baseline errors remain. Native results stay in RAM/display.

## Validation and packaging

Fresh raw payload5120 bytes is padded with0xCC to the retained9916-byte extent.
17 internal relocations include four absolute32 entries. Fresh checks pass:
131379 ownership cases, ASan/UBSan construction at four placements,12 diskless CPU
fixtures(all closed),144 instruction models,23 compiled nxdk page cases and372
compiled ownership cases. The models check exact write order, no retries, first/
last-read timing cases, dropped blank/restore stores, restoration after timer
faults, selector restoration, unchanged geometry/encoder registers, stack and
whole-framebuffer guards. These remain models, not physical scanout proof.

Exact sources/binaries are pinned; normalized published711 GPU helper sources
are the new build inputs.711's original executed snapshots remain unchanged.
Inherited build.py docstring says baseline-only; the compiled712 source and this
report define the expanded blank/restore scope. No functional driver fix claimed.

## Observation guide

Initial BLUE kernel picture lasts five seconds. Native top GREEN and second CYAN
precede the blank request. The screen should go black briefly, then return to the
same720p picture with a GREEN second bar, held for manual reset. ORANGE indicates
a returned rejection/failure; other pre-call PCI/timer refusal colors remain.
Record whether black and restoration were actually seen, not just the final bar.
A returned/held checkpoint is not a mode change or Windows1.6 qualification.
No startup hook, Windows launch or console C access. Consult actual launch and
collection receipts for runtime state; never retry an accepted launch.

## Closed physical result

One SITE accepted2026-10-27T05:54:36.333099Z. User reported GREEN holding, then
explicitly confirmed "Saw black, then picture returned." This supports the paired
blank/restore observation on this run at retained720p. It does not independently
separate the sequencer and ACPI gate effects or establish reliability.

After the user's confirmed manual power-cycle, nine preparation records were
collected once, read twice and audited. Last file phase is handoff_armed: these
are pre-transfer records, not native RAM results. PCI, CRTC, sequencer, geometry
and allocation mappings exactly match711. Independent alias/disjoint-range
checks pass; all source/binary/report pins and unrelated entries are unchanged.

712 is CLOSED. Console at dashboard, no startup hook or owned host process.
Manual reset is not a normal Windows shutdown. Native mode initialization and
Windows1.6 qualification remain unproved;708/709 exact failure stage remains
unknown. Next isolate the extended-register unlock/check after blanking, with
visible restoration before adding common setup, geometry or encoder writes.
