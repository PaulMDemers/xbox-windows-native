# Full image size does not prove both row parities are displayed

User notes that720p is clean,1080 output fills the screen without blank gaps,
one-row bands become a perfectly solid color, and an odd-row move swaps that
color. User confirms POUND external power is connected and points to its prior
successful use. That history supports compatibility but neither proves nor
refutes this specific1080i fine-detail failure. Adapter fault remains unproved;
another purchase is not a prerequisite to source/state investigation.

The programmed mode is1080i, not1080p. A conceptual mapping
D(y)=F(2*floor(y/2)+p), p=0 or1, preserves1080 output rows while retaining only540
independent source rows. All-black even rows expand to solidblack; shifting the
source by one row makes that same parity sample all-white. Magenta/green follows
the same math. No blank rows are required. This is an explanatory model, not a
measurement of the scanout implementation. Existing431motion002 tested512
positions; it was not rerun or reclassified.

If hardware is assumed electrically sound, candidate configuration/processing
causes are: repeated selection of one field's source rows because field addressing
or parity progression is wrong; a scanout vertical-scale/line-repeat setting that
selects alternate rows then expands them; or output interlace/field identification
that causes a downstream processor to keep or repeatedly select one parity.
Field-order reversal alone is a weaker explanation for stable single-color static
bands. Ordinary averaging of black/white rows would tend toward gray, not a stable
pure black or white. Ordinary both-field bob can itself expose alternating colors;
no temporal field-rate measurement currently distinguishes these possibilities.

Evidence excludes neither scanout programming nor external processing. Correct
CPU framebuffer bytes do not prove transmitted rows.430/432 record the base and
16RAMDAC values, not time-resolved field parity or the full CRTC/encoder state.
The Windows profile derives from earlier stock configuration captures, so matching
stock timing values is not an independent guarantee of correct field alternation.
The stock test does independently remove Windows drawing/Xromwell execution from
the failure path. The pinned nxdk function selects1080i mode0x880E0C03, allocates
1920*1080*4 bytes and passes7680-byte pitch into the stock kernel. No caller-side
half-height buffer or explicit two-row copy was found in this reviewed path.

Historical309 already captured CRTC/addressed encoder snapshots, with6c explicitly
unknown; review those before adding a diagnostic. The next useful software work
is decoding field/stride/line-repeat/interlace controls and designing a bounded
read-only temporal field-state observation, not changing a register on a guess.
Require documented register semantics and safe reads; distinguish memory pitch
from effective per-field row step. A full raster can still have half vertical
detail. Keep720p default and all closed trials unchanged.

Primary mechanism reference: Microsoft VMRDeinterlaceTech describes line
replication and vertical-stretch field expansion:
https://learn.microsoft.com/en-us/windows/win32/api/strmif/ne-strmif-vmrdeinterlacetech
This is not documentation of this TV, adapter, or NV2A implementation.

No hardware access, new native build, image editing, timing/filter patch or new
runtime experiment in433. No source files outside these notes were modified.
