# Current preparation

Fresh crash001 is being prepared. Never launch until before allocation,
configuration, pagefile map, exact helper/display pins and frozen preflight pass.
No physical action. Read DESIGN.md. Reuse the prior reviewed helper bytes; do
not rebuild the old copied Build.ps1/review.py as part of this test.

One-shot Run.ps1, observer trace.py and supervisor supervise.py own the new run.
Inspect actual records/sessions first; never duplicate launch or collection.
After closure run audit-crash.py once, configuration.py crash001 after and
cold-map.py crash001 after, record-closure.py, verify.py, verify-payload.py,
verify-render.py and verify-ram.py. Preserve any failure. Require manual visual
inspection of the captured emulator screen as evidence separate from cold bytes.
Never reboot the original crash image; recovery needs a separate owned child.
