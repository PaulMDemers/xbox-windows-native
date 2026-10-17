# 434: live raster cadence captured; row-fetch parity still unresolved

One new stock-kernel diagnostic was accepted at 2026-10-17 05:14:16 UTC and
collected after its requested firmware restart at 05:15:29 UTC. It completed
720p, 1080i and recovery 720p with error zero, 41,071 timestamped raster samples,
stable before/after register snapshots and zero native pixel mismatches.
All five private files were read twice and rehashed. The existing 720p Windows
launcher, startup and protected payloads remained unchanged. No Xbox C access,
Windows launch, driver replacement, encoder write or timing patch occurred.

| Observation | 720p | 1080i |
| --- | --- | --- |
| Legacy decoded memory pitch | 5,120 bytes | 7,680 bytes |
| CRTC active lines | 720 | 540 |
| Output timing active lines | 720 | 1,080 |
| Observed raster low-word range | 0..749 | 0..560 |
| Counter cycle cadence | about 16.667 ms | about 16.667 ms |
| Standard double scan / row repeat bits | off | off |
| NV04-named vertical-scale enable | off | off |

The 1080i wrap intervals alternate between shorter and longer groups, roughly
16.65 and 16.68 ms. This supports interlaced timing behavior; it does not prove
opposite source-row fetches. Sampling gaps were about 14.5 us and at most 17.5 us;
this is not a measurement of analog half-line sync edges. Raw bit 16 correlates
with blanking, not an independently established field identity. One internal
197-to-196 counter regression is retained in analysis001, separately from the
12 low-word cycle wraps. The original decoder's 13 raw decreases remain intact.

The full-screen symptom can still result from selecting alternate source rows
and expanding them. Correct pitch, full memory allocation and interlaced cadence
do not establish both output parities. The standard repeat/scale controls tested
here do not explain it. Neither the adapter nor the Xbox's remaining scanout/
encoder path has been exonerated or identified as the cause. No new visual
observation was requested for this short telemetry run.

The Conexant CX25870/871 manufacturer's Appendix E says its SD FLD_MODE setting
does not control HDTV field selection: 1080i requires the appropriate incoming
sync phase from the graphics controller. This is relevant to the unresolved
GPU-to-encoder boundary, but the console's exact encoder revision and complete
state are still not established. It is not permission to change that register.
Reference: https://dtsheet.com/doc/737283/conexant-cx25870

The reviewed nxdk video ISR does not alternate framebuffer row offsets. PBKit's
normal ISR swaps complete framebuffer bases; no explicit interlaced row-offset
toggle was found there either. Its initialization does change PCRTC_CONFIG's
address mode from the stock value 3 to 2. That is an untested difference, not a
diagnosed cause, and was not applied. Cxbx's GetDisplayFieldStatus emulation uses
an emulated vblank counter's parity; it is not proof of a physical field-ID bit.
See source-followup.json for exact source pins and NEXT.md for the comparison.

Build001 XBE: e221a9f3cf8bac33f1661519fe7c1260a3b60ad92c09b627111eacac614de8bf.
The shared SDK remained byte-identical; only its inherited export-section merge
warning appeared. Host002 rejects 79 synthetic transport mutations and actual
post-analysis rejects 54 header mutations. Host001's synthetic HDTV-pack enum
was wrong (1 instead of actual nxdk 4); review caught this before launch, original
inputs/results remain in prior-host001, and host002 corrects it. Review001's
source matcher mistook a pointer declaration for a register store; its failure
and original source are retained, with review002 succeeding independently.

Native pixel checks reuse the rendering helper; they are not an independent
full framebuffer capture. This is a successful scoped read-only observation,
not visual qualification, whole-disk integrity, Windows shutdown, a performance
result or a release gate. No emulator runtime was used to qualify raster timing:
the pinned xemu implementation increments its raster stub on reads. All host
commands are closed and the console returned to the dashboard. Never relaunch,
recollect or overwrite physical001.
