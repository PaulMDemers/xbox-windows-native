# Remaining qualification before hardware

Keep this ordinary matched pair immutable. Never relaunch or recollect closed
cases. Independent diagnostics live in separate video-ram-scanout kits; preserve
their failures and do not label their runs ordinary. The current physical
FATX0101/video0093 baseline and0.1.0 remain untouched.

1. Independent video-ram-scanout3 is now CLOSED PASS: twelve checkpoints/
   1,794,048pixels, full11940byte driver text,267pins, complete teardown and strict
   cold audit. Keep its two earlier failed observers closed and failed. This
   resolves the initial copy-path scanout gate, not complete DDI qualification.
2. Use a NEW bounded rendering workload to exercise the seven callbacks still
   unobserved: StrokePath, FillPath, StrokeAndFillPath, LineTo, Paint, StretchBlt,
   PlgBlt. Add pixel oracles for all fourteen paths, including currently observed
   incidental desktop text/alpha/gradient/transparency. Use real GDI APIs and
   observe actual routing; do not directly call hooks to manufacture coverage.
3. Cover complex/empty/offscreen clipping, masks and translations, non-copy ROPs,
   mirrored stretch, patterned brushes, transparent/opaque text, paths and alpha.
   Compare an independent DIB reference AND physical framebuffer; GDI readback
   from the private RAM primary alone is insufficient.
4. Review foreign device-surface ownership before widening scope. XwnOwner's
   current pointer equality relies on this one-display fixture. A foreign driver
   may also use dhsurf==dhpdev; do not cast that foreign private object blindly.
   A bounded registry of owned live PDEVs or equally explicit ownership scheme
   needs lifecycle/concurrency tests before printer/multiple-device support.
5. Test cursor shapes/movement/hide/show and exclusion across drawing regions,
   pointer restoration and primary readback. Current Eng pointer forwarding is
   exercised incidentally, not exhaustively qualified. Keep reentrancy visible;
   do not add a lock across an Eng callback without proving it can reenter safely.
6. Measure actual mode assert/disable/re-enable and bootvid handoff, including
   failure returns. Host fault shims are not NT5 lifecycle proof. Run a NEW
   sacrificial controlled-crash rendering/dump child using the already-qualified
   high-LBA stack; retain crash/recovery separation and all dump safety gates.
7. Only after these correctness gates, compare useful rendering performance.
   Full-clip uploads are conservative and may be slow. Optimize from measured
   dirty bounds/callback cost; keep permanentUC0106, no late WC alias changes.
   xemu timings do not establish Xbox speed. Hardware comes as a separate trial.

No new physical mode or Pinball/OpenGL support is claimed for this driver.
Higher resolutions and public/reproducible packaging remain later work.
