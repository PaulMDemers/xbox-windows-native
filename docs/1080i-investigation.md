# 1080i investigation handoff

Status as of October 17, 2026: **paused at the user's request; unresolved**.
Use **720p** for the working demo. No further display test is queued, and no
1080i fix or release qualification is claimed.

## Observed behavior

On the tested console, 720p has clean text and full-window dragging. At 1080i,
text loses fine strokes and dragged window contents appear to jostle. A pattern
of alternating one-pixel horizontal rows becomes a solid black or white region;
alternating magenta/green rows become a solid single color. Changing the source
row parity swaps the selected colors. Two-row stripes retain visible detail.
The picture still fills the display: this is lost row detail, not empty gaps.

The same symptom occurs in Windows and in a standalone nxdk program using the
stock Xbox video API. It was reported on a TCL 50S425 with Game Mode off and on
a second display, using the same externally powered POUND HD Link adapter.
The second display model, exact adapter revision and measured incoming HDMI
format were not established. The Xbox mode under test is 1080i; a reported
1920x1080 size alone does not establish progressive HDMI output.

## Evidence and its limits

| Comparison | Result | What it establishes |
| --- | --- | --- |
| Windows 720p versus 1080i | Text and dragging clean at 720p; defects at 1080i. Captured drawing/framebuffer pixels match at the checked points. | The visible defect can occur despite correct captured pixels; captures are not field-resolved output measurements. |
| Standalone stock video API | Correct independent pattern pixels; same reported 1080i artifact without Windows. | A Windows font or GDI defect is not required to reproduce this symptom. |
| Second display | Same reported artifact with the same adapter and console. | A cause confined to the first TV is less likely; adapter and Xbox output remain shared variables. |
| Read-only raster probe (434) | 41,071 timestamped samples across 720p, 1080i and recovery 720p. Correct decoded pitches: 5,120 and 7,680 bytes. | 1080i has a 540-line CRTC active area, 1,080-line output timing and roughly 16.667 ms counter cycles. This does not prove alternating source-row fetches. |
| Normal PBKit initialization (435) | Watched orange-before/cyan-after comparison shows the same defect. All 2,097,152 captured pattern pixels match in each of two runs. | Normal PBKit initialization did not restore fine detail on this setup. |

In the PBKit comparison, all four phases used the same framebuffer allocation,
physical address and pitch. Among the 23 CRTC and 29 MMIO registers captured,
only `PCRTC_CONFIG` changed, from 3 to 2. This was **not** a one-register
experiment: normal PBKit initialization also changes graphics, interrupt, gamma
and other state, including registers outside that inventory. Copying the value
2 into the Windows driver is not a demonstrated fix.

The raster probe found the reviewed double-scan, row-repeat and NV04-named
vertical-scale controls off. Its short/long cycle alternation is consistent
with interlaced timing, but sample uncertainty prevents an analog half-line
measurement. Raw bit 16 was correlated with blanking, not proved to identify
field parity. An internal counter regression is retained in the raw analysis.

## Conclusions

- Selecting one source-row parity and expanding it explains the full-sized
  picture, solid one-row bands and parity-dependent color swaps. This is an
  explanatory model, not a measured internal implementation.
- The evidence points toward scanout or field handling after framebuffer
  generation. It does not locate the producer in GPU memory fetch, GPU-to-encoder
  synchronization, adapter conversion or display processing.
- Neither an adapter fault nor correct Xbox field generation has been proved.
  The results also do not establish that this loss is unavoidable for 1080i.
- Font smoothing, outline dragging and the PBKit address-mode setting are not
  demonstrated repairs for the 1080i output. Outline dragging remains an optional
  desktop preference; full dragging already works at 720p.

## Resume criteria

Resume with a test that distinguishes stages of the field/output path, rather
than another broad rendering change. Useful evidence would be an independently
validated field-resolved capture or a controlled alternative component/HDMI path.
A software probe needs an explicit interpretation and actual hardware evidence
for any field identifier it uses. Do not guess an IRQ row-offset toggle or apply
an SD-only encoder control as an HDTV fix.

Keep the working 720p installation and rollback files unchanged. Closed attempts
and their failures are retained; any future physical run needs a fresh output
directory and its own launch/collection records. Pausing this investigation does
not qualify 1080i or change the separate installation/release gates.

## Detailed records

- [Windows pattern comparison](../outputs/field-scanout428/)
- [Stock video API comparison](../outputs/stock-field430/)
- [Earlier photo analysis](../outputs/field-photos431/)
- [Second-display comparison](../outputs/display-compare432/REPORT.md)
- [Row-selection hypothesis review](../outputs/field-hypothesis433/REPORT.md)
- [Live raster timing and source limitations](../outputs/field-timing434/REPORT.md)
- [PBKit comparison and capture checks](../outputs/pbkit-compare435/REPORT.md)
- [Requested watched rerun](../outputs/pbkit-compare435/RUN002.md)
- [Final visual result](../outputs/pbkit-compare435/VISUAL002.md) and
  [four photo hashes](../outputs/pbkit-compare435/visual002.json)

Earlier frozen records saying the visual answer was pending describe their
publication time. The final visual addendum resolves that question: no
improvement after PBKit initialization. Original photos remain private.
Both PBKit runs completed and returned to the dashboard; all owned host commands
are closed. No physical driver, startup, default resolution or Xbox C change was
made by these comparisons.
