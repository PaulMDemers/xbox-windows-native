# Photographs resolve the affected bands

The user supplied four photographs from the original Windows428 test and said
the stock430 effect was the same. These photographs are Windows evidence; they
are not photographs of the stock test. Original attachment hashes and manual
observations are recorded in analysis001.json. Images remain private and were
not edited or committed. No hardware access, launch, build or settings change.

| Photograph | One-line stripe area | Two-line stripe area | Parity marker |
| --- | --- | --- | --- |
| 1 | Outside the crop | Mostly outside the crop | Magenta |
| 2 and 3 | Appears solid black | Horizontal stripes remain visible | Magenta |
| 4 | Appears solid white | Horizontal stripes remain visible | Green |

The least-significant binary row-label band also appears black in2/3 and white
in4. Therefore the observations are not explained solely by the intentionally
solid higher binary-label columns. The important missing spatial detail is in
alternating horizontal rows, despite the panels themselves being vertical.

The independently generated428 pattern has these exact relationships when
selecting every second source row: black one-line area pairs with magenta and
black row-bit0; white pairs with green and white row-bit0. The two-line area
still alternates black/white under either selection. All four combinations of
phase0/1 and source-row parity satisfy this arithmetic model. This is a model
demonstration and manual visual comparison, not an automated fit or measurement
of photographed screen pixels.

This is strongly consistent with one row parity dominating a displayed instant,
as can happen with single-field expansion, bob deinterlacing, line decimation,
or camera sampling of a field-based output. It does NOT prove one electrical
field is permanently missing, identify field order, or distinguish the Xbox
encoder from the HDMI adapter or TV. Unknown camera exposure, test phase and
window position prevent assigning a fixed source parity/field number. The
user's live report and unchanged720p comparison make it worth investigating
display processing, but still photographs cannot establish temporal behavior.

The user then clarified a LIVE observation: "when the test moves, the green
column alternates between green and purple. the black/white columns flash".
This rules out the camera as the sole explanation. In the actual428 moving
phase, source pixels stay unchanged while the window top is32+(step*3)%64.
Every move changes the top-row parity. A fixed screen-row-parity sampler therefore
alternates black/magenta and white/green as the window moves. motion002 checks
512 modeled positions across both possible sampler parities. This explains the
observed relationship without claiming that exact sampler is installed: bob or
motion-adaptive processing can also make fine detail unstable. No frame/field
frequency or electrical field ordering has been measured.

Microsoft documents [bob line replication and field stretching](https://learn.microsoft.com/en-us/windows/win32/api/strmif/ne-strmif-vmrdeinterlacetech)
as ways of reconstructing absent lines from an individual field; that explains
why such processing can produce jagged detail. This reference describes a
mechanism, not the algorithm installed in this TV or adapter.

Combined evidence:428 actual framebuffer/shadow checks and independent pixels
passed at both modes;430 stock-kernel mode API also returned correct pixels,
with the same visual effect reported without Windows. This supports investigating
the shared interlaced output path before modifying GDI/font rendering. Fourteen
stock RAMDAC registers matching profile constants do not prove every Windows
CRTC/encoder register or outgoing field is correct. No1080i qualification.

The user confirmed the adapter connects directly to the TV. There is no reported
receiver, HDMI switch or capture device between them. TV make/model and exact
adapter identity remain unknown. Windows remains configured for720p; all prior
runtime cases remain closed and their immutable reports are unchanged.
