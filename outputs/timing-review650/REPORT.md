#650: programmed timing review; failing native readback remains missing

This is an offline review, with no new build, console contact, startup hook,
emulator or runtime reuse.649 remains CLOSED. Its wait3/second-pair-clear result
and broad unsigned timer category remain observations, not a diagnosis.

## Result

The intended480p constants have no newly identified vertical-range error. The
decoder agrees with all114 applicable retained readback comparisons across the
successful stock631 low/high/low sequence, using the established masks. The
entire480p profile also matches632's programming facts. These comparisons do
not show that a failing native launch accepted the same values.

| Programmed counter interpretation | 480p | 720p |
|---|---:|---:|
| Visible lines |480|720|
| Vertical total |525|750|
| Vertical retrace start |488|724|
| Following retrace end |494|729|
| Retrace span in counter lines |6|5|
| Pitch bytes |2880|5120|
| CRTC horizontal total,8-dot arithmetic |832|1640|
| Separate FP horizontal total+1 |858|1650|

The horizontal totals differ between CRTC and FP blocks in both profiles and
the retained successful stock readings. Do not make them equal as a speculative
fix.480p's FP_HCRTC is671 while its visible endpoint is719; that difference also
exists in the stock facts/readback. These are different register fields, not
interchangeable width or clock values. No physical frequency is derived here.

## Register semantics and reference quality

The addressed block is0x601000 with byte access at offset0x3da. The wrapper adds
GPU base0xfd000000. It uses the first block without a second-head displacement;
this establishes the software address, not live output routing.

[Nouveau v6.12 nvreg.h](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/nvreg.h)
defines this address separately from PCRTC interrupt status0x600100. Its CRTC
field definitions place CR25 bit4 in horizontal blank-end bit6 and CR2d bit0 in
horizontal-total bit8; CR25 bits2/3 extend vertical retrace/blank starts. CR41
contains higher vertical bits. The decoder follows those placements. Uncaptured
CR41 in631 is explicitly unknown, not silently reconstructed as zero.

[Nouveau crtc.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/crtc.c#L345-L413)
provides the corresponding encoder assignments. The programmed values decode
without double scanning, with sync enabled and the interlace register at0xff.
These interpret programmed fields; they are not measurements of effective clocks.

[Envytools' PCRTC page](https://envytools.readthedocs.io/en/latest/hw/display/nv3/pcrtc.html)
has conflicting CR25 descriptions: it swaps the vertical-start extensions and
assigns bit4 to horizontal total. That prose is not used for decoding. Current
progressive profiles have the disputed vertical extension bits clear; synthetic
one-bit tests nevertheless cover them so the disagreement cannot pass unnoticed.

[Nouveau hw.c](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/hw.c#L747-L757)
polls bit3 at this status address for retrace. Its sequencer handling also uses
bit5 of SR1 for blanking. Both profiles request SR1=1 before the edge loop, so
the software does not intentionally leave that bit set while polling. Actual
readback and NV2A-specific internal routing remain unmeasured.

The [Video Seven VGA technical reference](https://www.bitsavers.org/components/video7/700-0242_V7_VGA_Technical_Reference_Manual_Jun88.pdf)
describes VGA status bit3 as vertical retrace and documents that reading the
status resets the attribute-controller index/data toggle. This is a VGA-family
reference, not an NV2A specification. [Nouveau's attribute accessors](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/hw.h#L193-L235)
read this status before index/data access, corroborating that access convention.
Calling every status read entirely side-effect-free would therefore be wrong.
The adapter finishes attribute writes before its edge loop, with no later
attribute pair interleaved; no such collision is apparent in this source.

The public references do not establish all NV2A status routing,0x680630 format,
or0x6806a0 handshake semantics. A similar-generation register name is not
permission to clear a bit, change a clock, select another head or skip a wait.

## Transaction order and what is still unknown

Pinned633 and instrumented649 have the same functional write ordering:

1. Read retained VPLL0x680508 and PCRTC_CONFIG0x600804; blank via0x80d3/SR1.
2. Wait for equality of bits0/4 at0x6806a0 before changing the profile.
3. Program framebuffer, initial FP control, encoder reset/table, clock-select OR,
   FP/MMIO fields, sequencer/graphics/attribute fields and CRTC table.
4. Write the opposite bit0 request to0x6806a0; request SR1=1; enter six edge waits.
5. Only after all waits, write final0x680880, finish encoder6c/ba, verify geometry
   and pitch, then unblank output with0x80d3=4.

There is no post-request0x6806a0 readback in that path. The entry equality test
cannot prove the new request completed. The retained clock/config readings are
RAM-only in the failing native run. The first successful clear/set pair followed
by a failed clear wait proves sampled predicates only: it does not by itself
prove a complete frame, continued scanout, or which timing source was active.

The later output-control writes are indeed behind the poll. That makes ordering
worth observing, but does not prove circular dependency: this path has also
succeeded on hardware. The initial/final0x680880 values differ by0x00020011;
generic field names are insufficient to decide which dependency applies here.
No output-control reordering or functional patch was made.

The existing RAM trace captures the status byte but the LEDs do not expose it.
An all-ones status value would also satisfy the failed-clear predicate. Neither
all-ones reads nor stopped scanout has been observed. A useful next diagnostic
must distinguish those possibilities and record masked readback at named stages.

## Evidence and limits

decode.py pins the exact633 profile source, extracts its literal arrays without
executing source, compares632 facts and the retained631 records, and decodes the
programmed counters. decode001.json retains the results and unmasked differences.
CR19 low bits and CR2d upper bits differ in stock readback; established masks
remain intact. This is not fresh hardware evidence or a complete register audit.

test_decode.py checks independent numeric expectations, isolated extension bits,
modular endpoints and missing/out-of-range refusal. sources001.json pins inputs
and retrieved Linux references. Reference retrieval failures are retained in
reference-limitations001.json. No proprietary code, media or binary is published.

The next step is specified in NEXT.md. Normal720p/startup were not contacted or
changed. Last observed console state remains649's dashboard return. Automation
is paused; no new hook, process, lease acquisition or hardware launch exists.
