# Video and platform development after 0.1.0

User priorities: faster window dragging, additional Xbox modes including 1080i,
documented FATX/platform findings, and convenient root-menu Windows launch.
User also confirms working ping. Preserve the release before driver changes.

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
