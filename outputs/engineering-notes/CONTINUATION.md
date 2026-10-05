# Continuation: repeat-boot miniport qualified on hardware

Updated2026-10-05 after two normal physical restarts. Candidate0093 remains
installed; normal startup is restored and the Xbox is at UnleashX. No emulator,
observer, build, automation or queued Windows test remains running.

Evidence: outputs/video-trace-reuse-settled/qualification.json and physical.json.
Both hardware cycles passed graphics checks, normal shutdown, expected payloads,
valid trace, no new popup/unexpected error. Launches were22:15:47.892872Z and
22:18:01.946565Z. Cycle2 used cycle1's exact trace with no host reset. FATX/HAL/
loader and1024x576x32 geometry unchanged. No third launch. Existing trace file
is still required; this change removes the one-shot contents restriction only.

Candidate SHA256:3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf.
Source tree329a29d61af1620a9fc005b0d8fcfb9e1a937d20; patch/input/build/compiled-test
reports live in outputs/video-trace-reuse. Hardware rollback copy:
/F/winnt/system32/drivers/xboxvnt5.trace011. Private verified driver/rollback ZIP:
E:/Codex-archive/xbox-windows-native/postrelease-video-reuse-20261005.
SHA256:44c613e74b8a82e1494cc60140e3ceee27d53df4762e1ede97e22800242857e5.
No archive restore test claimed; v0.1.0 tag and full recovery bundles unchanged.

Retain rejected0092: xemu passed but hardware STOP0xB4, then verified rollback.
Retain the two0093 strict emulator popup failures. Captured and rebuilt controls
passed; older qualified Paint logs also contain that exact intermittent shutdown
popup. The later clean-start two-boot candidate run passed the FULL strict audit,
and that result was the hardware gate. No popup waiver was used. Starting clean
then reusing its own output does not establish a cause for the earlier popup.

Next work is video performance: audit actual framebuffer cache attributes and
aliases, then implement/test one isolated change against bounded physical GDI
baselines. No rendering speedup or HD mode is part of0093. Keep storage0088.

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

1. Repeat-boot maintenance is complete for two bounded physical boots. Keep0093
   installed and preserve the trace file. Do not deploy0092 or disable the broad
   trace/PnP flags. Further removal of file I/O is a separate unqualified change.
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
