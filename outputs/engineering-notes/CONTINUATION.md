# Continuation: candidate0098 fixes post-install image checksum failure in xemu

Latest work: outputs/video-nt5-load-trace and outputs/fatx-paging-eof.
All three debugger attempts and both ordinary emulator runs are closed. No owned
emulator/helper is running. No physical access or deployment occurred. Hardware
remains video0093/FATX0088; release0.1.0 is unchanged.

Evidence chain: GPU service was requested, but MmLoadSystemImage rejected
xboxvnt5.sys before DriverEntry. Verified NT5 kernel tracing exposed underlying
STATUS_IMAGE_CHECKSUM_MISMATCH (0xc0000221), converted to 0xc000026c. Both captured
42,215-byte miniport mappings match the exact file hash within EOF; their byte at
EOF is 0x97 from sector slack. NT5 sums a rounded-up word count. Isolated replay of
its checksum instructions returns false with that byte and true when only it is
zeroed. The image's stored checksum is already correct; do not patch/bypass it.
The tracer's last-image hint is not thread-aware; mapped-482.bin is another image.

0098-vfat-paging-eof-zero.patch zeroes only returned regular-file paging bytes
past logical EOF, within the caller's mapped buffer and under existing paging
resource protection. Directory/FAT/raw-volume streams and nonpaging reads are
unchanged. Completion length is retained. No disk-slack rewrite is introduced.
Fresh pinned RosBE build, FATX profile with _WIN2K_COMPAT_SLIST_USAGE:
source tree 873d6b4ff9505e71da119abd99aba301013e1749
xwnfatx.sys SHA256 beeaf329f0446d3bdd2ed490fa8143888253115c0ff6c1662b67b82e6619eedd.
Paired host compilation of the actual common-read functions: old fails 10/63,
fixed passes 63/63 with buffer guards, short/failure and metadata exclusions.
Host tests do not establish NT ABI/cache/concurrency behavior.

Ordinary runs (only FATX payload changed; miniport0096/display0097/INF retained):
- fatx-paging-eof001: Start=1 diagnostic parent; strict cold audit PASS.
- fatx-paging-eof002: actual installed Start=3 parent; strict cold audit PASS.
Both complete four graphics correctness stages and five timing loops, normal
restart, matching payloads, no new popup or unexpected event error. Binding/INF/
owned display file are intact. Start=3 works with the EOF fix. These fixtures
retain earlier audio failed-install flags and the synthetic xemu PCI model.
No full allocation audit or broad hardware/persistence qualification in this turn.

Next: poisoned-tail real mapped-file tests across sector/page/cluster boundaries,
then broader persistence stress and a controlled hardware trial. Do not deploy
0098 automatically from two short emulator passes. Continue display PnP stop/
remove/restart ownership and consumer quiescence separately; higher video modes
and physical performance remain later gates. Preserve the existing physical and
release recovery bundles.

Exact fixture/build/audit hashes and cleanup in fatx-paging-eof/summary.json,
fixture-001/002.json, inputs.json and build-report.json. Guest disks/backing chains
remain local and unmoved. Closed trace RAM and older CPU logs are hash-verified
under E:/Codex-archive/xbox-windows-native/closed-load-evidence-20261006; original
and archived paths are in video-nt5-load-trace/evidence-archive.json. The former
video-nt5-display-package crash decoder now supports --ram for archived captures.
Shared FATX engineering/skill notes contain the EOF/slack lesson; installed skill
matches the versioned source. Latest owned cleanup: 2026-10-06T01:05:25.4311025Z.

# Continuation: display INF installs, subsequent boot fails0xB4

Latest work: outputs/video-nt5-display-package. Five emulator attempts are closed;
all cold audits are complete. No owned test process remains running. No physical
access or deployment occurred; candidate0093, FATX0088 and release0.1.0 remain
unchanged by this work. Neither0096 nor0097 nor the new package is promoted.

The authored INF targets PCI10DE:02A0. Existing0096 miniport and0097 display bytes
are unchanged. It uses the NT5 SoftwareSettings contract and a project-owned
xwnfb.dll filename. Original xboxvnt5.inf is retained for failed-attempt replay;
xwnvideo.inf is the current experimental source. Both are original text; owned
Windows media/binaries, fixture disks and crash RAM remain ignored/private.

-001: updater startup reached a desktop with overlapping wizard/welcome/console.
 No installer log persisted. Guest input attempts had no visible effect; stopped
 for inspection, not normal shutdown. No installation success inferred.
-002: preloaded DevicePath selects the INF, but replacing protected framebuf.dll
 elevated signing policy to Warn. Graphics and normal restart passed, no popup;
 registration incomplete, strict FAIL.
-003: changed only package DLL name/token to xwnfb. SetupAPI completes full install,
 query-removal veto requires reboot, ConfigFlags=0, Driver points to display0001,
 oem2.inf matches staged bytes, Device0 selects xwnfb. Graphics/payload/restart
 checks pass, one shutdown popup makes strict FAIL. Service Start changed1->3.
-004: boot from003's installed state, no guest edits. STOP0xB4(0,0,0,0x50000).
 Kernel RAM decode has VIDEOPRT but no Xbox miniport/display in loaded modules.
 PnP service binding exists with problem0; this does not establish driver startup.
-005: isolated child restores only active-control-set XboxVnt5 Start3->1;
 all5725 keys/17547 values compared. Start1 persisted, but same0xB4 and missing
 loaded miniport. Reject the simple start-type remedy. No normal shutdown in004/005.

Next: trace the actual image-load/device-add path in a fresh owned diagnostic run.
next-probe-plan.json pins matching NT5 kernel hash, public RVAs and entry bytes for
IopLoadDriver, MmLoadSystemImage, IopInitializeSystemDrivers and IopCallDriverAddDevice.
Resolve the actual next-run kernel base; do not reuse prior absolute addresses.
Determine whether service/image loading is skipped, fails, or unloads before GDI.
Keep debugger evidence separate from ordinary validation. Do not deploy an INF
workaround or treat ConfigFlags/Driver presence as functional PnP qualification.
Generic stop/remove/restart ownership and consumer quiescence remain outstanding.

Artifacts: immutable fixtures/seed hashes in fixture-001..005.json; current
reproducible installed-state parent is video-nt5-display-package-004.qcow2;
005 changes one start value. Keep all QCOW parents. Failed boot RAM captures are
artifacts/reboot-crash.ram and artifacts/starttype-crash.ram. Offline decoded
kernel/module/PnP reports are004/crash.json and005/crash.json. Page directories
were recovered from self-references, not captured CPU CR3; shared kernel data only.
Latest owned cleanup:2026-10-06T00:40:11.9405634Z. Shared skill installation and
source/report checks passed; commits include the installation/protection lessons.

# Continuation: ordinary installer-isolation experiments

Latest work is outputs/video-installer-isolation. No physical access or deployment;
candidate0093 and normal startup remain the last hash-verified hardware baseline.
All three owned emulator runs completed normal restarts and are closed. Their
cold audits and comparison are complete; no owned test process remains running.

- audio003 changed only ConfigFlags for the observed01B0 failed installation.
  All5722 hive keys and17533 values were compared, allowing exactly one value
  addition. Graphics, hashes, UC mapping and restart passed; strict audit failed
  with one popup. SetupAPI advanced from01B0 to01B4.
- control003 used the identical immutable0096/0097 fixture and unchanged SYSTEM.
  It passed the strict ordinary audit with no popups, while01B0 installation was
  still pending. This confirms intermittency; it prevents calling the flag a fix.
- pair004 changes only01B0 and01B4 failed-install flags. It passed the strict
  audit with no popups and returned at2026-10-06T00:01:51UTC. Its next installer
  target was02A0, the GPU itself. SetupAPI reports no compatible driver, while
  baseline enum metadata has Service XboxVnt5 but no Driver value (flags0x400).
  Boot-time binding is working; complete PnP driver installation is missing.
- Prepare001/002 did not boot. Absent-value lookup and the shared output-path
  guard rejected those attempts before guest hive writes. Artifacts retained.

The registry flags are diagnostic interventions, not audio support, a driver
correction or a deployment recipe. Do not promote them based on a clean boot.
No cache/mode/storage changes. Free host C: space was20.28GiB after these runs.
Keep all QCOW backing parents. Full miniport PnP stop/remove/restart ownership
and consumer quiescence remain separate requirements before promotion.

Next concrete task: inspect/package a proper NT5 display INF for02A0, matching
the installed service/display binary contract, then test real installation in a
new owned fixture. Do not suppress installation of the GPU with FAILEDINSTALL.
Retain original boot bindings and rollback; installation may invoke the still
unqualified PnP stop/start paths. A clean control is not a reason to waive popup
checks. The shared skill now records this setup-vs-boot distinction and the
need for target-process address-space reads; structural validation passed.

## Previous display and shutdown work

Physical0093 remains installed with normal startup. No physical access occurred
in the work below; the last hardware hash verification is23:07:22UTC Oct5.
Release0.1.0 and FATX0088 are unchanged. Neither0096 nor0097 is promoted.

New emulator evidence, Oct5:
- video-startup-detached: unchanged0096,120-second settling, startup CMD exits
  before shutdown. One ordinary strict audit PASS, with four GDI copy checks,
  five timing loops, UC RAM mapping, payload hashes and clean normal restart.
- video-surface-lifecycle: new0097 ReactOS display replacement. Fresh source tree
  a0a3f8b6bbd9c4fb60042554dd6d24130b0afddf; compiled failure-injection tests PASS.
  DLL SHA2563d4c5c2659c06f9ae4c9a735a99ad972d4e773e02a0f1b7d4d8c2d18053e9db7.
  Ordinary GDI/payload/mapping/restart checks passed, but two rundll32 shutdown
  popups made the strict audit FAIL. Detaching startup is not a general fix.
  Run nt5-video-surface-lifecycle-001 closed at23:37:47UTC. Its fixture002 and
  failed unbooted fixture001 remain preserved. The full DLL uses two clusters;
  a stripped version lost nonpaged section flags and was rejected, never booted.
- The installed framebuf.dll is Microsoft5.00.2180.1, not the ReactOS source.
  provenance.json and baseline-ddi.json separate these implementations.0097 fixes
  source-level failure cleanup, not an established defect in the installed DLL.
  Its public baseline callback table has no BitBlt/CopyBits rendering callbacks.
- video-shutdown-exits captured25 NtTerminateProcess calls, but unresolved target
  handles; video-shutdown-targets watched the wrong PspTerminateProcess site.
  Both debugger runs had clean cold checks, but are explicitly unqualified for
  ordinary boot because pauses alter timing. Historical failures remain retained.
- video-shutdown-resolved-targets resolved a CSRSS termination target as
  rundll32.exe newdev.dll,DevInstall for PCI10DE:01B0. SetupAPI confirms PID932
  and driver-selection error0xe0000228; its registry description is Multimedia
  Audio Controller. This unfinished installer was alive at shutdown. The traced
  run had no popups and clean cold checks, but ordinary_boot_qualified=false.
  It does not prove the popup cause. Owned cleanup completed at23:42:59UTC.
  All owned emulator, supervisor, debugger, audit and build processes are closed.

Immediate next work: inspect the unfinished01B0 install queue and its shutdown
interaction in an ordinary reproduction before promotion; then
complete miniport PnP stop/remove/restart ownership and consumer quiescence.
0097 covers surface failure unwind and normal release, not full PnP lifetime.
Retain0093 and unchanged cache policy; no measured speedup or HD-mode change.
Host C: had about20.6GiB free after the build. Twelve closed owned CPU logs were
losslessly compressed; backing parents/source caches were not removed. Check
the actual host free space before another fresh20GiB-preflight build.

## Previous mapping investigation

Physical candidate0093 is restored. Final read-only FTP verification at
2026-10-05 23:07:22 UTC passed for video, FATX0088, HAL, loader, launcher,
pre-dim backup and normal startup. Evidence: outputs/video-mapping-audit/final-baseline.json.
No emulator, observer, debugger, build or automation remains running from this work.
All owned sessions have closed; backing chains and source caches remain in place.

0094 observed UC GPU-aperture mappings on both emulator and Xbox; known loader
alias endpoints were absent. Emulator strict audit passed. Physical graphics,
payload and normal restart checks passed, but strict qualification failed on two
rundll32 shutdown popups. Logs retained and0093 restored; no performance claim.

0095 direct RAM through VideoPortMapMemory failed before desktop in xemu:
STOP E0580001 (7,57,03c00000,00400000), ERROR_INVALID_PARAMETER.
This failure is preserved;0095 was never deployed to hardware.

0096 uses owned MmMapIoSpace(MmNonCached) with reference/unmap/unload cleanup.
Fresh reconstruction and compiled execution checks passed. Source tree:
eded91e06d6cac60a1cf66bc8a05117ebfa6a71a; miniport SHA256:
e8021879bd606eb9cfc6927fbf50565c41781779af86e56f4678fa890b6eb6ec.
Both ordinary emulator runs passed pixel, direct-RAM UC, payload and normal
restart checks, but strict audits failed on two rundll32 shutdown popups.
Changing settling from30 to120seconds did not eliminate the failure.
See outputs/video-direct-map and outputs/video-direct-map-settled.
No0096 hardware deployment or measured hardware speedup occurred.

Exploratory nt5-video-shutdown-probe-001 used the same binary and120-second
protocol. Initial debugger handshake timed out and paused the guest; the corrected
handshake resumed that same guest. No NtRaiseHardError event was captured before
the supervisor closed the returned emulator. Cold logs show the same two popups.
Debugger timing interference disqualifies this run as ordinary validation;
outputs/video-shutdown-probe preserves both attach failure and final observations.
Cleanup completed at23:05:47 UTC; no popup root cause has been established.

Immediate next work:
1. Trace the shutdown popup creation path; the NtRaiseHardError breakpoint did
   not capture it. Do not select a clean timing retry as proof of a fix.
2. Complete PnP stop/remove/restart mapping lifetime, including consumer quiescence
   and asynchronous completion. Normal unmap/unload alone is not a general driver.
3. Re-run strict ordinary emulator checks, then one bounded physical timing trial
   with rollback. Keep0093 and release0.1.0 intact. No HD-mode change yet.
4. C: last measured about19.7GiB free. Fresh source builds require20GiB preflight;
   review safe archival of closed artifacts before another build. Never remove
   QCOW backing parents or unreviewed source caches to make room.

0093 physical qualification: outputs/video-trace-reuse-settled/qualification.json
and physical.json, two clean cycles at22:15:47.892872Z and22:18:01.946565Z Oct5.
SHA256 3e74a5c35b68d7fa0e047b4ba9cec25e7ec0ea5a94e796fc07508f667fcc85cf;
source tree329a29d61af1620a9fc005b0d8fcfb9e1a937d20. Normal startup restored.
Private verified overlay: E:/Codex-archive/xbox-windows-native/postrelease-video-reuse-20261005,
ZIP SHA256 44c613e74b8a82e1494cc60140e3ceee27d53df4762e1ede97e22800242857e5.
No archive restore test claimed. Retain0092 physicalSTOP0xB4 and prior0093
strict popup failures; later clean-start/reuse0093 passed without any waiver.

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
  without filesystem repair or a global reset. C: had about24GiB free after
  that retry; the latest reading is about19.7GiB (see above). New builds check actual Windows backing-volume space,
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

Host C: free space is about19.7GiB after these builds. The20GiB fresh-build
preflight should block additional source builds until reviewed artifacts can be
archived safely; no backing chains or source caches were removed.
