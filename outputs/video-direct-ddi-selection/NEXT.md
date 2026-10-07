# Next: controlled RAM-primary prototype

All runs in this kit and ../video-direct-ddi are CLOSED and audited. Never reuse
attempt IDs, rerun collections, or base a new test on a completed guest disk.
Keep the unused immutable prepared fixture as the parent, with explicit input
and backing-chain hashes. Keep current physical0101/video0093 untouched.

The direct0107 baseline is now qualified for54drawing cases/162pixel stages.
Before promotion, add independent scanout comparisons and broader DDI coverage.
Follow ../video-late-cache-review/SHADOW-PLAN.md in a NEW source tree/kit:

1. Retain permanentUC0106 mapping and the qualified storage/network stack. Build
   an opaque driver-managed primary plus private RAM bitmap; no late cache/PTE
   transition or mixed UC/WC aliases. Keep a direct rollback. Check complete
   allocation before publication and reverse failure cleanup.
2. Introduce synchronous uploads only after engine drawing finishes. Implement
   primary-source/destination substitution, overlap, clipping, translation, masks
   and non-copy ROPs. Cover CopyBits/BitBlt, text/path/line/stretch/alpha/gradient
   fallbacks explicitly; unhooked writes must not bypass the upload boundary.
3. Measure actual callback coverage and pointer hide/show/move/exclusion. Keep
   unsupported DirectDraw access from bypassing the shadow; do not assume old
   Pinball/OpenGL observations qualify the new path. Do not hold a drawing lock
   across an engine callback that can reenter it without proving its behavior.
4. Compare independent physical framebuffer bytes as well as GDI readback.
   Host failure tests and ordinary pixel tests cannot alone prove scanout
   coherence. Separate debugger observations from ordinary workload qualification.
5. Repeat strict event/cold gates, mode/disable lifecycle and new sacrificial
   crash rendering check before considering a physical test. Only then compare
   performance on matched inputs; current copy timings are not hardware speed.

Keep mandatory identity gating. Any future selected display must be named in both
bound class Settings and service Device0 values; validate the exact current-
control-set delta and runtime identity, not just one registry value.
