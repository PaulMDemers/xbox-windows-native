# Video and platform development after 0.1.0

User priorities: faster window dragging, additional Xbox modes including 1080i,
documented FATX/platform findings, and convenient root-menu Windows launch.
User also confirms working ping. Preserve the release before driver changes.

## Next gate after FATX0098 qualification (2026-10-06 UTC)

The focused [physical0098 trial](../fatx0098-physical-trial/README.md) passed.
The completed [third timed soak](../fatx0098-soak3/README.md) passes its full
900000ms workload,527 mappings,16 BMP API replays and cold integrity checks:
50 exact files,34 absent intermediates,consistent full allocation,3439 binary
hashes and nine structural hives. Strict qualification remains FAIL because of
one recurrent rundll32 shutdown popup and three Srv2013 warnings. Normal startup
is restored; no recovery capture or further video change followed. Investigate
the installer/shutdown path and warning sources before another strict test.
Actual user application observations remain from earlier runs and are separate.
FATX0098/video0093 is the current physical combination.
The [late creation trace](../shutdown-createprocess/README.md) isolates an
invalid-handle return from CreateProcessAsUserW after its inner creation succeeds.
The cleanup status5 is a fixed constant, not the original failure. PnP saved-token
lifetime is the next investigation target; no popup reproduced in these debugger
controls, so this is neither a fix nor authorization to waive the soak failure.
Two [token-lifetime traces](../shutdown-token-lifetime/README.md) now locate
umpnpmgr's close of the saved token while the installer thread is still using it.
One passes zero after the clear; the reduced-observer run initially validates the
token, then sees it invalidated during creation. Both cleanly shut down without
the popup, so the remaining gate is correlation with the actual hard error in the
previously failing workload, not another graphics deployment or identical soak.
The follow-up [shutdown diagnostic](../shutdown-diagnostics/README.md) confirms
Windows F:/G:/H: map to dashboard C:/X:/Y: and report0.56%,2.89%,6.18% free;
the large boot/data partition is not the warned volume. A clean two-minute
physical diagnostic still had the unsupported01B0 installer wizard open, while
the clean emulator observation still had the GPU wizard open. Pending installer
presence alone therefore does not explain the intermittent popup. Trace creation/
exit ordering across shutdown before changing device policy. These observations
do not waive the original full-soak event failures or qualify a new video mapping.
The installed-package emulator boots in [fatx-paging-eof](../fatx-paging-eof/README.md)
pass with0098 for both the actual Start=3 state and the diagnostic Start=1 state.
This resolves the demonstrated EOF/checksum loading failure; it does not qualify
video performance, mode changes or generic stop/remove/restart ownership.

After the soak and fresh recovery capture:

1. Re-run a matched graphics baseline using the existing pixel-checked probe on
   the current physical0093 mapping and fixed mode. Keep actual window-drag
   observations separate from the five microbenchmark operations.
2. Rehearse a single mapping change with0098 in a fresh owned fixture. Keep the
   Microsoft display DLL for the mapping comparison if that combination passes;
   do not substitute the0097 DLL and attribute the whole change to mapping alone.
   Compare actual first/last PTE addresses and cache policy, four pixel stages,
   unchanged payloads, normal restart and event deltas. Preserve any popup failure.
3. Before generic use of the owned mapping, settle consumer teardown and pending
   PnP IRP completion. The0096 helper covers map/unmap/unload; its unload comment
   is not independent evidence that every drawing consumer is quiescent. Never
   free a live mapping merely because STOP/REMOVE was requested.
4. Use a separately identified bounded physical timing trial only for an eligible
   candidate, restore0093 afterward, and compare like-for-like geometry. A gain
   must coexist with correct overlapping copies and clean persistence/events.
5. Pursue cache/shadow-surface or GPU-copy work according to the measured result.
   Higher modes remain a separate boot-handoff project: first480p/720p, then1080i,
   with explicit encoder/cable/reservation checks and a working recovery mode.

The following evidence is historical; its then-current FATX0088 references do
not describe today's installed filesystem. Failed runs remain failures.

## Installer ordering evidence (2026-10-06 UTC)

[Three owned traces](../shutdown-installer-trace/README.md) all shut down cleanly;
they do not qualify a fix. The second directly captures services.exe attempting
the01B4 installer after CSRSS terminates the01B0 installer during shutdown.
Relative process parameters had obscured the next command; the host decoder now
handles them with matched-binary proof. Inspect the late CreateProcess failure
and window-station path next. No new physical deployment or registry policy edit.

## Current evidence

Physical GDI003 and both candidate0093 repeat-boot runs pass the four pixel
checks and five bounded timing loops. Their256x128 samples show much slower
framebuffer readback/overlap copies than fills/uploads, but do not measure window
dragging FPS or prove a cache cause. Candidate0093 resolves repeated-boot trace
contents maintenance and remains installed; it adds no rendering optimization.
0094 now records physical first/last desktop PTEs and PAT: GPU aperture
0xF3C00000..0xF3FFFFFF is UC. Known loader alias endpoints are absent; this is
not an exhaustive alias inventory. Its pixel/hash/shutdown checks passed, but
strict physical audit failed on two rundown-time rundll32 popups, and0093 was
restored. See ../video-mapping-audit and ../video-trace-reuse-settled.

0095's direct RAM address was rejected by VideoPortMapMemory in xemu (error87),
so it was never deployed.0096 owns an MmNonCached mapping with explicit reference
and unload cleanup. See ../video-direct-map for actual validation status. The
first question is whether the GPU aperture, rather than direct reserved RAM,
adds meaningful read latency while cache policy remains unchanged. Do not claim
a speedup before physical measurement or promote on a visible desktop alone.

0096 passes pixel/address/UC checks in two ordinary emulator boots, but both
strict audits fail on identical shutdown popups (30/120-second settling).
Hardware deployment remains gated. Complete stop/removal/restart ownership
before promoting the mapping helper; current code covers unmap and unload.
The separate breakpoint run is diagnostic only and captured no hard-error call.
A read-only FTP check at23:07:22UTC Oct5 confirmed0093, FATX/HAL/loader and startup
restored. No physical access occurred in the subsequent experiments.

The detached startup protocol now passes one ordinary strict emulator run with
unchanged0096 and120-second settling. Two later debugger runs also had no popups,
but are diagnostic only. These results support a launcher timing hypothesis;
they do not identify the popup cause or erase the synchronous failures.
See ../video-startup-detached and ../video-shutdown-exits.

0097 is a separate ReactOS display replacement with mapping failure unwind and
surface-before-mapping release. Its compiled failure-injection tests pass; see
../video-surface-lifecycle for runtime results and limits. The installed display
DLL is Microsoft's5.00.2180.1, not the ReactOS source. No source-level leak is
established in the installed binary. Full miniport PnP lifetime remains open.

The resolved-target debugger identified a live rundll32 newdev installer for
PCI10DE:01B0 at shutdown. SetupAPI confirms no compatible driver; its registry
description is Multimedia Audio Controller. That diagnostic run had no popups,
so this is a specific lead, not a demonstrated popup cause. Investigate the
pending installation queue before changing more video behavior; retain strict
ordinary checks. See ../video-shutdown-resolved-targets.

Ordinary isolation now advances the installer from01B0 to01B4, then to02A0
(the GPU), when only the selected failed-install flags are acknowledged. The
audio-only case had one popup; the unchanged control and two-device case were
clean. This remains intermittent. The GPU has a working boot service binding
but no Driver value, and SetupAPI cannot find a compatible package. The next
implementation is a matching NT5 display INF and real installation in an owned
fixture, with existing binaries preserved. Do not hide this by marking the GPU
failed-install. See ../video-installer-isolation for the exact comparison.

## First implementation: measure the existing drawing path

Build a bounded Windows 2000 GDI probe that records device caps/mode enumeration,
opaque fills, system-memory-to-screen copies, screen-to-memory copies and
screen-to-screen copies including overlap. Use a private visible window, check
API returns and GdiFlush, and write results outside the timed sections. Separate
emulator correctness from physical timing. Have no auto-reboot and no mode change.
Render a known pattern and validate copied pixels in the correctness pass.

Record dimensions, stride if available, bpp, batch size, elapsed time, repeat
count and candidate hashes. Verify that GdiFlush drains the client batch; it is
not a universal fence for a future asynchronous GPU implementation. Benchmark
one candidate at a time at identical geometry. Window-drag measurements need
separate end-to-end testing; a fast BitBlt microbenchmark alone is insufficient.

Baseline miniport `xboxvmp/nt5/xboxvnt5.c` maps memory with
VIDEO_MEMORY_SPACE_MEMORY. The experimental ReactOS framebuf/surface.c creates
an Eng bitmap with hook flags zero; this is not the installed Microsoft DLL's
source. Executing that binary's public DrvEnableDriver registration shows no
DrvCopyBits/DrvBitBlt callbacks (../video-surface-lifecycle/baseline-ddi.json).
Actual desktop mappings were measured UC. Do not enable write combining on conflicting physical
aliases or assume emulator speed predicts physical memory behavior.

## Optimization sequence and acceptance gates

1. Establish the baseline with the probe and repeated real window dragging.
2. Audit framebuffer mapping/cache attributes and aliases across loader, HAL,
   bootvid, miniport and display driver. Evaluate safe write combining and/or
   a cached shadow surface with dirty-region copies as separate experiments.
   Shadow copies consume scarce RAM; framebuffer reads may still be slow.
3. Evaluate overlap-correct CPU copies, fills and pointer handling. Retain GDI
   fallbacks for unsupported ROPs, clipping, formats and translations.
4. Only then consider NV2A 2D copy/fill acceleration. That requires explicit GPU
   ownership, bounded FIFO waits, synchronization with CPU accesses, reset/recovery
   and correct overlapping blits. It is not a small flag change in the miniport.
5. Isolate and remove diagnostic/PnP dependencies independently of performance
   changes. A smaller normal driver must reproduce the hardware boot success.

Every candidate needs compiled/API tests, an ordinary emulator boot, painting/
scrolling/overlap checks and normal restart/cold checks before physical promotion.
Require measurable improvement without corruption, cursor trails, hangs or
storage regressions. Keep a separate baseline launch path and known hashes.

## Mode work: 480p, 720p, then 1080i

The current driver retains one firmware mode and reports 60 Hz without a full
encoder/field-timing model. Merely adding modes to enumeration does not program
the hardware. nxdk's `lib/hal/video.c` contains HDTV 480p, 720p and 1080i entries,
gated by AV pack/region/capability selection; use it as a documented reference,
not an assumption that its Xbox-kernel APIs exist after NT takes over.

At 32 bpp, tightly packed single surfaces require:

| Geometry | Bytes | MiB | Fits current 4 MiB reserve? |
| --- | ---: | ---: | --- |
| 640 x 480 | 1,228,800 | 1.172 | Yes |
| 1280 x 720 | 3,686,400 | 3.516 | Yes, before alignment/extra surfaces |
| 1920 x 1080 | 8,294,400 | 7.910 | No |

1080i is a real target, but needs a coordinated framebuffer reservation/mapping
change across launcher/loader, HAL memory descriptors, bootvid and miniport.
Interlacing does not halve the stored full-frame pixel count. Encoder type,
AV cable, region/EEPROM flags and display compatibility must be detected or
recorded; don't advertise a mode that cannot be set. Model field/frame timing
and the interlaced flag correctly. Preserve a low-resolution recovery path.

Begin with explicit boot-time mode selection and a known fallback rather than
runtime switching while surfaces remain mapped. Validate pitch, format, offsets,
reserved extent, cache aliases and memory pressure. A full 1080i32 buffer leaves
less RAM for Windows; RGB565 would reduce memory but requires a separately
implemented/tested format path. Do not quietly reduce color depth in 0.1.0.

720p is the first HD test because it fits the present single-buffer byte budget.
That arithmetic is not a claim of working 720p: encoder setup, alignment and
all handoff mappings still need validation. Do not change dashboard video
preferences as a substitute for implementing Windows mode support.

## Other work queues

- Network: ping now user-confirmed. Record reproducible ICMP and checksum-verified
  file-transfer tests; test concurrent storage and CPU pressure separately.
- Audio: physical playback with a known waveform, then longer playback/load.
- Storage: retain0088; longer mixed-use/repeated-boot qualification and format/
  name boundary tests. Revisit the single Paint freeze if evidence recurs.
- Power: explicit electrical power-off and reset behavior without corrupting
  pending writes; retain normal shutdown completion evidence.
- Linux handoff: review the FATX invariant/test notes, prepare a small synthetic
  corpus with no proprietary files, and share only when the user asks to send
  or publish it. No claims that another project's driver has our exact bugs.

## Primary references

- [Microsoft DrvCopyBits contract](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvcopybits)
- [nxdk video implementation](https://github.com/XboxDev/nxdk/blob/master/lib/hal/video.c)
  (local pinned reference 58427c078b4ccb0121f359b6b6c536b3b2914976).
- Pinned ReactOS source and this repository's 0074/0075 patches; preserve the
  upstream notices and version-specific NT5 ABI checks.
