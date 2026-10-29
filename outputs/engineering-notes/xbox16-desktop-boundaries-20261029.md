# Xbox 1.6 desktop integration boundaries, October 29

Source review only, after host qualification of Test811. No new hardware access,
driver patch, mode admission, or Windows result follows from this note.

The current Windows miniport already describes one retained 32-bit framebuffer.
Nt5VideoInitialize reads visible bounds, CRTC13/19 pitch, CRTC28 format and scanout
base, checks the reservation/aperture, and exposes one mode. SET_CURRENT_MODE
accepts only that mode and does not program the encoder. FreeLoader similarly
reads the established layout and initializes its framebuffer console. Therefore
getting a trustworthy display into the loader is a separate milestone from
adding Windows mode switching or acceleration. It does not establish that the
existing miniport will work unmodified on 1.6; that needs the actual boot test.

The qualified Xromwell HD adapter requires encoder value 0 and cable enum 3.
That path is not Xcalibur support. Its explicit 480p wrapper refuses fallback;
its historical 720p wrapper can return to legacy initialization on unsupported
admission. The legacy initialization contains CR1b, CR22 and CR33 writes whose
behavior cannot be imported blindly from source. The current preserving probes
intentionally exclude those writes after the observed restoration failures.

## Remaining source boundaries

| Boundary | Current limit and next evidence |
| --- | --- |
| CR09 line-compare bit 6 | 809 refused CR22 FA before setup. Cold810 pending confirmed power cycle. Native811 is host-qualified only. Same-value 40-to-40 cannot prove a bit transition. |
| CR18 line-compare low byte | Next GPU helper write after CR09; source target FF. Own before/after/restore and neighbor checks are still needed. |
| CR1A repaint | Source target 04 for widths below1280, otherwise00. Separate reversible and combined-state evidence remains. |
| CR25 overflow | The GPU helper computes horizontal/vertical overflow bits after repaint. Must account for the complete byte and retained pitch interpretation. |
| CR28 format and CR2D high horizontal bits | Last two helper writes; source targets depend on pixel depth and horizontal total. Their later-prefix behavior is not admitted by the current CR09 probe. |
| Complete mode transaction | CR39/scanout, Xcalibur transport/table, VGA sequencing, output enable and settlement must be validated as a coherent transaction with independently checked geometry and a stable visible pattern. Earlier individual evidence is not a complete native mode pass. |
| Loader integration | Adapt a proven transaction to the actual reserved framebuffer, physical/virtual mappings, CPU state and failure path. Do not copy an nxdk-owned buffer address or borrow a running firmware mode as Windows proof. |
| Windows desktop | Fresh owned fixture/build, stage/readback, one watched boot, verify colors, pitch, bounds, mouse/text, persistence and normal restart; retain original Conexant720p regression evidence. |

The remaining work is several distinct integration gates, not merely two more
registers or a percentage-complete estimate. Completing the scalar checks can
reduce the search space, but encoder/output interactions may still require new
diagnostics. No 3D or accelerated capability is implied.

## Next action

When the user is back, obtain the requested ten-second cold power-off and
UnleashX confirmation for810. If its actual raw result is PASS, admit811 using
its frozen controller. If810 again refuses, preserve the refusal and investigate
the starting state instead of repeating launches. Keep all closed attempts closed.
