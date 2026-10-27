# Current status and guide map

Reviewed October 26, 2026 against the retained evidence through kernel allocation preflight693 (UTC October27).
This page summarizes supported observations; individual reports retain their
original failures and scope. For the exact active attempt and next engineering
step, read [CONTINUATION](../outputs/engineering-notes/CONTINUATION.md) and
[STATUS](../outputs/engineering-notes/STATUS.md).

## Choose a guide

| Goal | Start here |
| --- | --- |
| Build the open-source drivers and bootloaders | [Component builds](building.md), then [build to boot](build-to-boot.md) |
| Assemble the two transferable ZIPs | [Kit assembly](build-test-kits.md); Windows preparation is a separate prerequisite |
| Inventory another Xbox or copy a reviewed package | [Tester quick start](testers.md) and [compatibility matrix](console-compatibility.md) |
| Run the configured development installation | [Installation and first boot](installation.md#already-configured-demo) |
| Select a boot resolution or recover it | [Display configuration](display-configuration.md) and [experimental selector](display-selector-recovery.md) |
| Build and check software graphics samples | [Sample ladder](graphics-samples.md) |
| Understand RCT behavior and performance evidence | [Compatibility](rct-compatibility.md), [measurements](rct-performance-plan.md), [recording](rct-recording.md) |
| Find archived local artifacts | [Artifact archive and restoration](ARTIFACT-ARCHIVE.md) |
| Understand our emulator patches | [Local xemu changes](xemu-changes.md) |

## What works, and what remains open

| Area | Current evidence | Boundary |
| --- | --- | --- |
| Development Xbox | Native Windows 2000 at 720p on the original 64 MiB Conexant console | Boot intermittency remains; a dashboard return does not prove normal Windows shutdown |
| Current source verification | All eight profiles verify after 677 reconciled four stale launcher pins and its reference tree | Two fresh launcher builds and six compiled-wrapper fixtures passed; default remains 720p. No physical deployment or gate waiver; see the [build boundary](building.md#current-checkout-launcher-pins-reconciled) |
| 480p | Separate 720×480×32 boot profile passed drawing, dragging, typing, save/reopen and later 720p readback in [638](../outputs/windows480p638/REPORT.md), [642](../outputs/windows480p642/REPORT.md), [643](../outputs/windows720p643/REPORT.md) | Selector apply/readback and recovery passed, but its 480p boot failed in [645](../outputs/display-selector645/REPORT.md); live Windows mode changes and automatic selection remain unimplemented |
| RCT Deluxe | Windowed title/park/building, manual save/load and arrow-key/right-button scrolling on the development console; [626](../outputs/rct626/REPORT.md) confirms the later interactive session and cleanup | Window-edge scrolling stays still; fullscreen unqualified; sound deferred; no Xbox game FPS measurement |
| Software D3D7 | Scoped offscreen and windowed RGB-renderer samples pass through combined scenes; sustained synthetic scene has Xbox clock checks | Exact ideal alpha endpoints remain failed; perspective interpolation has PC results only; synthetic timings are not game FPS |
| Native GPU acceleration | No accelerated driver installed | Game rendering, a module name or software sample success is not NV2A acceleration |
| Other Xbox revisions | User-identified 1.6: [composite kernel baseline682](../outputs/composite682/REPORT.md) displays proper bars and returns automatically; [HDMI720p baseline683](../outputs/hdmi683/RESULT.md) also passed | [686](../outputs/encoder686/REPORT.md) adds a positive Xcalibur-address response. [689 native preflight](../outputs/xcal-visible689/REPORT.md) held solid amber/black without its success indication; phase unknown, manually reset. No native display or Windows qualification; this unit's GPU field differs from inventory630 |
| Packaging | Hardware-info utility and private prepared E/720p Windows ZIP recipes and [delivery587](../outputs/delivery587/README.md) | RCT excluded; private Windows assets are not public downloads; clean physical provisioning remains incomplete |
| Installation/storage | Component builds and scoped prepared-image/emulator restore checks pass | Six clean-media FATX long-name exclusions, crypto failures and strict event failures remain; selected-file audits are not whole-volume health checks |

## Current engineering boundary

[PC628](../outputs/rct628/REPORT.md) measured a verified paused park for about
20 seconds and identified one captured `timeGetTime` caller. It does not establish
Xbox costs, game FPS, a polling fix or a native acceleration result. The bounded
physical game-cost comparison remains outstanding. Compatibility work on other
revisions is intended before acceleration. The user now has an incoming 1.6;
kernel video baselines are active on that console, ahead of native integration.

Earlier networking/timer work is **tabled**, with [679's local package preserved](../outputs/revision680/REPORT.md)
and no pending launch. [678's host-only full-firmware timer integration](../outputs/timer678/REPORT.md)
compiled a private XBE and passed 25 isolated full-image function fixtures;
there was no console launch or installed change. It preserves the existing
capture and encoded packet, then runs the bounded timer probe and halts without
calling the sender. Timer and SMC behavior are unchanged. The prior physical 674
capture received no UDP datagrams; the user saw lights off on a black screen and
then manually reset the console. Those observations do not identify a timer,
SMC or network root cause. It is no longer the next physical test.

The composite480i baseline682 and HDMI720p baseline683 are collected, with user
observations and matching kernel geometry reports. Native Xcalibur integration
and a separate pattern-only qualification remain next. The separate
681 prototype passed 66,164 modeled protocol/profile cases and four compiled
legacy GPU geometry fixtures. It does not establish physical output: native
encoder qualification, native integration and Windows handoff remain to be completed.

The ordinary 720p configuration remains the baseline. 1080i is tabled, Ftdisk49
and shutdown-popup limitations remain recorded, and closed test identities must
not be rerun. Historical `outputs/` records and old bundle instructions describe
their frozen packages; use the maintained guides above for new work.

The new [read-only video prerequisite684](../outputs/video-clock684/RESULT.md)
measured a timer rate consistent with3.375MHz and two clear SMBus status snapshots
on this unit. [Binding685](../outputs/xcal-binding685/REPORT.md) uses that rate and
passes33 compiled32-bit port/delay fixtures. No native encoder transaction or
Windows test follows from those results; this does not resume networking.

[Encoder probe686](../outputs/encoder686/REPORT.md) got a successful kernel read
at the Xcalibur address and failed reads at the older encoder addresses. This is
positive presence evidence, not a unique chip ID. [Entry687](../outputs/xcal-entry687/REPORT.md)
adds bounded cable/video readers and demonstrates why inserting them after the
legacy EEPROM reader can encounter inherited completion status. Its48 compiled
fixtures and two sequence models pass; actual native handoff and encoder output
remain unqualified. The [next integration plan](../outputs/xcal-entry687/NEXT.md)
preserves status ownership and precedes a separate watched native pattern trial.

[688](../outputs/xcal-native688/REPORT.md) links the bounded reads before legacy
C startup and passes27 full-image function fixtures. [689](../outputs/xcal-visible689/REPORT.md)
adds a bounded success signal and passes32 host cases, but its watched physical
run showed solid amber/black and required a manual reset. That does not locate
the stopping point or qualify native reads. The console returned to the dashboard
and its staged files matched. Next is an early checkpoint independent of SMBus;
no identical retry or encoder programming is planned from that observation.

[690](../outputs/framebuffer690/REPORT.md) confirms the kernel PCI/cable/settings
match689 expectations and validates an owned720p framebuffer across900 pages. The
user saw the panels and automatic return. This does not prove post-handoff state
or native writes; follow [690 NEXT](../outputs/framebuffer690/NEXT.md) for the
framebuffer custody and full assembly-path review before another native launch.

[691�693](../outputs/handoff-preflight693/REPORT.md) identify a concrete candidate
loader defect: the kernel can round the virtual reservation base, while the old
wrapper reuses it as the physical execution address. Compiled failure models and
actual kernel rounding agree on that risk.693 keeps those addresses separate and
passes physical dual-copy/guard/cleanup checks. It has not entered native code,
fixed the ordinary boot path or qualified Windows1.6; [native transition validation
is next](../outputs/handoff-preflight693/NEXT.md).
