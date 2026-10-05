# Continuation after physical GDI retry 002

Updated 2026-10-05. Physical driver/loader baseline remains 0.1.0. One physical
GDI retry was accepted at 21:17:54 UTC and has not returned to dashboard FTP
within the four-minute observation. A screen-state question is pending; do not
infer a crash or relaunch. Only new /F/xwngdi02 helpers and test startup changed.
Collect attempt002 must restore original startup first when dashboard is available.
Attempt001 was collected at 21:17:26 UTC: original startup restored, no probe or
runner log, byte-identical before/after Windows event logs, baseline unchanged.
The user reported Xromwell hanging with their "razor chroma ornata" keyboard
attached, unplugged it and manually rebooted before requesting this retry.
That peripheral observation is not a diagnosed USB cause or Windows GDI failure.
All owned emulator/build/observer processes are closed; no automation is running.
Private repository visibility and v0.1.0 tag identity remain unchanged.

## Results

- Added one-command native reconstruction/package tooling. Pipeline002 completed
  fresh source replay, seven native components, Cromwell launcher and verified
  eight-file overlay. It is not a Windows installer. The complete overlay now
  passes one emulator boot/GDI/restart and cold byte/event checks in
  outputs/rebuilt-overlay-validation. Broader/physical qualification is pending.
- HAL reconstruction now explicitly enables FRAMEBUFFER_ONLY_PCI as required by
  the qualified physical artifact. The later live CMake cache was misleadingly
  OFF. Builds001-004 remain compilation evidence, not baseline-equivalent.
- Repeated package assembly from identical inputs is byte-identical. Fresh
  compilation is not yet byte-identical. FATX/video/network/boot-video .text
  matches captured baseline. Exact tested-package comparison attributes all HAL
  code differences to relocation slots; two rosload non-pointer differences are
  diagnostic line-number constants. Pointed data is not fully normalized.
- GDI v2 failed due to startup-dialog occlusion. V3 enforces visibility and
  passes all four copy checks, including both overlap directions. One emulator
  launch, normal runner restart, dashboard return and cold EVT6006 verified.
  Qualified FATX/video hashes unchanged. See outputs/video-next/probe-v3.
  Timings include host build activity and are not Xbox performance evidence.
- Shared xbox-native-bringup skill updated and structurally validated. FATX
  notes, public-release plan, and xemu patch inventory remain available from
  the root README. No upstream submissions or public visibility change.

## Host incident and retained artifacts

- Pipeline001 filled C:; WSL fell back to read-only. Archived 46 closed owned
  CPU logs to E:/Codex-archive/xbox-windows-native/trace-archive-20261005 with
  SHA256 verification. Original run folders contain cpu-trace.archive.json
  pointers. No QCOW backing chain was relocated. Ubuntu then mounted writable
  without filesystem repair or a global reset. C: has about24GiB free after
  the successful retry. New builds check actual Windows backing-volume space,
  not only Linux virtual capacity. Keep watching host space before more fixtures.
- Failed pipeline001 checkout retained at
  /home/paul/xbox-windows-native/build/package-reconstruction-001.
- Successful one-command output:
  /home/paul/xbox-windows-native/build/package-reconstruction-002.
  Private overlay copy: E:/Codex-archive/xbox-windows-native/reconstructed-overlay-20261005.
  ZIP SHA256:5ada6fb5887227f4c4b50d2197bb7a498342b4cd2f4eab90d81716990d5d30e3.
- Earlier reconstruction001-005, launcher-reconstruction-001 and overlay001/002
  retained under the same native build root. Do not reuse attempt identities.
- Closed owned GDI runs: nt5-gdi-baseline-001 (old failure), -002 (occluded),
  -003 (PASS). Fixture parents and children remain at original paths.
- Verified 0.1.0 recovery bundles remain at
  E:/Codex-archive/xbox-windows-native/0.1.0; no restore was performed.

## Next actions

1. Resolve physical-gdi-002 screen state. When dashboard FTP returns, run
   outputs/video-next/physical-gdi-002/trial.py collect with existing FTP env,
   then qualify.py. Collection restores startup before reading logs. Do not
   overwrite trial.json, erase attempt.log or issue a second Windows launch.
   Preserve failures; request manual reboot only after the screen is understood.
   Attempt001 is complete and unexercised; do not recollect or reuse its identity.
2. Use physical timings only if correctness and normal shutdown qualify them.
   Review framebuffer cache/stride/copy paths before changing acceleration.
   Extend the reconstructed overlay's storage/network coverage in a new fixture;
   its current bounded emulator PASS does not establish hardware equivalence.
3. Complete local user-media assembly and toolchain environment pinning for a
   fresh reproducible installation; full OS packaging remains open.
4. Plan 720p then1080i after console revision and cable/HDMI adapter are known.
   Coordinate loader/HAL/framebuffer reservation/miniport. Current HAL BAR2
   suppression is a compatibility workaround, not an accelerated GPU contract.
5. Prepare sanitized public export with per-component licensing and private
   history review. Prepare focused xemu reproductions against current upstream;
   no submission until the concrete proposal is reviewed with the user.

UnleashX root Windows entry was installed previously with backup/readback.
Dashboard visibility is not user-confirmed; do not reinstall it to refresh notes.
