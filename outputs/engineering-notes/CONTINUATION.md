# Continuation after diagnostic trace correction and GDI retry003

Updated 2026-10-05. Physical driver/loader baseline remains 0.1.0.
Attempt002 is collected: startup restored, no runner/probe logs, event logs
unchanged, all baseline/helper hashes intact. User photo shows the deliberate
E0580001(0D,4,C000003E,10) diagnostic trace guard. Preserved trace has41 old
records and its first nonzero byte after the marker at offset16. The new GDI
harness omitted the known preserve-and-reseed step; it is now corrected.

Attempt003 accepted at21:25:15 UTC, dashboard return21:26:47 UTC, collected and
qualified PASS: four pixel checks, five timings, normal runner restart/EVT6006,
unchanged drivers/helpers and no unexpected new warning/error or popup. Normal
startup is restored. No observer/emulator/build/automation is running. Private
repo and v0.1.0 tag unchanged. See physical-gdi-003/next-boot.json for the exact
one-boot diagnostic-seed readiness state; no extra Windows launch was issued.

Attempt001 was a user-reported Xromwell hang with their "razor chroma ornata"
keyboard attached; they unplugged it and rebooted. It never exercised the probe.
This peripheral report is separate from the trace-seed cause of attempt002.

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

1. Remove the one-shot trace dependency before unattended manual-menu boots.
   Keep required PnP/geometry behavior, isolate logging changes, test at least two
   ordinary emulator boots without host reseeding, then qualify on hardware.
   Preserve 0.1.0 rollback; no changed driver is physically deployed yet.
2. Use physical003 as one bounded baseline: fill/upload2.10/2.36ms, readback50.14ms,
   overlap56.67/29.71ms for256x128. Investigate cache aliases/stride/copy paths;
   this does not measure dragging FPS or prove a cache cause. Extend reconstructed
   overlay storage/network coverage in a new fixture. Its current emulator PASS
   does not establish hardware equivalence. Never reuse attempts001-003.
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
