# Continuation after release/build preparation

Updated 2026-10-05. Physical 0.1.0 baseline remains unchanged and the Xbox was last
reported on the dashboard. No console test, deployment, reboot or emulator launch
was performed during this preparation. No automation or build is left running.

## Completed

- Installed `xbox-native-bringup` in the shared skills directory, validated with
  skill-creator, and linked it from homebrew-console-dev. Its versioned copy and
  installation hashes are under `outputs/developer-skills`.
- Added an xemu patch/evidence inventory in `outputs/upstream-xemu`: Cromwell
  MMIO alignment and TX batching are candidates; the NV2A resource experiment is
  diagnostic only. Existing upstream issues 2305/2910 are recorded. No contact
  or submission made, and no shared Linux project files changed.
- Added public-release plan and read-only history inventory under
  `outputs/public-release`. Private repository visibility and v0.1.0 tag unchanged.
  Public source licensing, personal-data review and sanitized export remain open.
- Added `tools/rebuild-native.py` with pinned patch inputs, exact source-tree
  verification, parameterized paths and independent fresh build profiles.
  Three fresh builds completed filesystem, loader, second-stage loader, HAL and
  working-configuration video miniport. Two-build comparison finds small binary
  differences; deterministic binaries and full bootable package creation are
  not yet established. No reconstructed output has runtime qualification.

## Retained artifacts

- Private recovery archives: `E:/Codex-archive/xbox-windows-native/0.1.0`; five
  verified archives, hashes and recovery instructions under release-0.1.0.
- Native Linux source/build/log/cache/artifact directories:
  `/home/paul/xbox-windows-native/build/reconstruction-001`, `-002`, `-003`.
  Each is an owned independent fetch/build; original live source/build trees
  were not modified. Compact reports are in reproducible-build. Retain them for
  binary-difference analysis; no need to archive duplicate full source copies.
- Video fixture and run `nt5-gdi-baseline-001` remain closed and preserved.
  Its pixel tests failed; do not reuse its identity or call its timings a valid
  benchmark. The failure has not established a display-driver regression.

## Next actions

1. Refine the GDI probe: dedicated window, settled desktop, DIB-to-DIB first,
   upload/readback next, directional overlap last; log first mismatch and RGB.
   Validate the probe before modifying the video driver. Use a new owned fixture.
2. Resume framebuffer/cache/stride and software copy profiling, then evaluate
   accelerated drawing. Cable/HDMI adapter and console revision answer remains
   pending for mode work. Stage 720p before 1080i; reserve/handoff memory jointly.
3. Extend the builder to Cromwell, remaining installed custom drivers and config
   packaging, then user-provided local media assembly. Pin the whole toolchain
   environment and explain the current small binary differences before stronger
   reproducibility claims. Keep deployment an explicit separate action.
4. Prepare a small sanitized public source export with component licensing and
   focused tests. Do not flip repository visibility or rewrite frozen history.
5. Prepare current-upstream NVNET regressions and hardware-comparison tests,
   preserving the shared Linux project's ownership and existing evidence.
   Review a concrete proposal with the user before actual upstream submission.

UnleashX root Windows entry was installed previously with backup and readback;
visibility after dashboard reload is still not user-confirmed. Do not reinstall
it or start Windows just to recheck this note.
