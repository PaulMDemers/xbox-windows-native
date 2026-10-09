# Corrected actual-input-clip oracle

This unique206 kit replaces204's unsupported full-client byte expectation with
actual205 input-clip metadata. The prior204 failure is preserved unchanged; its
candidate was never launched. Version11 probe retains the13 real text cases and
all prior copy/DIB/window/profile/visibility/installation/restart gates.

The160-byte118 packets surround only the target text call plus GdiFlush, with no
logging between. Client origin and dimensions are logged beforehand. C and an
independent Python pixel-membership loop count the actual input clip intersected
with the known app region; ON also intersects the conservative string/opaque
bound. Both implementations must equal the actual row-copy byte accumulator.
The input metadata is captured before rendering and atomically published with
that call, without holding the accounting lock across rendering or copying.

Viewport-edge cases compare against a256x128 DIB and client readback; they do not
claim physical-screen-corner or additional-mode coverage. Every case separately
requires whole RAM-primary/scanout equality, including pixels outside that DIB.
Font metrics must confirm italic/underline/strikeout coverage. GDI may implement
the empty opaque call through BitBlt; zero text calls are accepted only for that
case and it still requires real changed pixels and exact readback/coherence.

Both temporary drivers use the same miniport, boot-video, captured physical-core
fixture and exact202 runner/201 bounded helper/194 guards; no synthetic device
policy is imported. Both new fixtures use xwntxt206 namespaces, standalone copies
on E and unique nt5-text206 owned run IDs. The draft namespace pins were preserved
and corrected before any fixture preparation or launch; see preparation-namespace-review.

Whole-boot errors remain strict failures. Equal copied bytes is a valid negative
optimization result; compare.py requires complete functional/cold scopes and
explicitly marks optimization_demonstrated/physical_testing_ready false in that
case. No timing comparison from emulator runs establishes hardware speed.
