# Native Xcalibur480p integration gates

Networking is tabled. Start with680's watched kernel-assisted baseline when the
incoming1.6 is ready. Neither681 nor679 authorizes a launch on stale readiness.

1. Establish actual board/cable/HD configuration and baseline visible colors,
   geometry and input format. Do not identify Xcalibur merely by failed probes.
2. Implement a new native binding for the tested block protocol with bounded
   polling and an independently validated500µs delay. Capture initial status,
   transaction result and exact failed register; do not silently acknowledge
   unknown pending work or skip a failed write. Test actual32-bit compiled code,
   port widths, all bounded exits and timer wrap/stall before an XBE launch.
3. Integrate an explicit Xcalibur-only480p profile in a fresh pinned Xromwell
   source tree. Include known source-derived common GPU setup, output conversion,
   exact allocation and readback checks. Preserve the maintained Conexant
   default and strict manifest. Reject unsupported configurations before mutation;
   any partial failure must stop before Windows. No legacy fallback as success.
4. First native hardware candidate is pattern-only and watched with reset
   available. Do not start Windows from this first encoder trial. Confirm RGB
   bars, stability, borders, stride and readback without firmware-state borrowing.
5. After that qualification, build a separately pinned Windows480p package with
   consistent Xromwell/FreeLoader/HAL/framebuffer contracts. Test desktop/input,
   save/reopen, normal restart and file/hive readback. No720p or live-mode-switch
   claim follows from480p success; RCT/acceleration come later.

All681 host fixtures are closed. Read their records, never rerun their identities.
New code/tests require a new attempt/output. No console contacted, no hook,
no running host process and no active build lease from this work.
