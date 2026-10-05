# Continuation after package and GDI probe validation

Updated 2026-10-05. Physical 0.1.0 remains unchanged; no hardware access this
turn. The private repository and v0.1.0 tag remain unchanged in visibility/tag
identity. All owned emulator and build processes are closed. No automation is
running for this work.

## Results

- Added one-command native reconstruction/package tooling. Pipeline002 completed
  fresh source replay, seven native components, Cromwell launcher and verified
  eight-file overlay. It is not a Windows installer and has no runtime
  qualification. Reports: outputs/reproducible-build/pipeline-002*.json.
- HAL reconstruction now explicitly enables FRAMEBUFFER_ONLY_PCI as required by
  the qualified physical artifact. The later live CMake cache was misleadingly
  OFF. Builds001-004 remain compilation evidence, not baseline-equivalent.
- Repeated package assembly from identical inputs is byte-identical. Fresh
  compilation is not yet byte-identical. FATX/video/network/boot-video .text
  matches captured baseline; HAL/rosload differences still need investigation.
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

1. Profile physical baseline with the visibility-controlled GDI probe. Keep
   timing runs free of unrelated host work; record physical results separately.
   Review framebuffer cache/stride/copy paths before changing acceleration.
2. Investigate HAL/rosload binary differences, then boot the reconstructed
   eight-component overlay in a new owned emulator fixture. Compilation alone
   does not authorize claiming hardware equivalence. Preserve current baseline.
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
