# Current status and guide map

Reviewed October 26, 2026 against the retained evidence through attempt 678.
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

## What works, and what remains open

| Area | Current evidence | Boundary |
| --- | --- | --- |
| Development Xbox | Native Windows 2000 at 720p on the original 64 MiB Conexant console | Boot intermittency remains; a dashboard return does not prove normal Windows shutdown |
| Current source verification | All eight profiles verify after 677 reconciled four stale launcher pins and its reference tree | Two fresh launcher builds and six compiled-wrapper fixtures passed; default remains 720p. No physical deployment or gate waiver; see the [build boundary](building.md#current-checkout-launcher-pins-reconciled) |
| 480p | Separate 720×480×32 boot profile passed drawing, dragging, typing, save/reopen and later 720p readback in [638](../outputs/windows480p638/REPORT.md), [642](../outputs/windows480p642/REPORT.md), [643](../outputs/windows720p643/REPORT.md) | Selector apply/readback and recovery passed, but its 480p boot failed in [645](../outputs/display-selector645/REPORT.md); live Windows mode changes and automatic selection remain unimplemented |
| RCT Deluxe | Windowed title/park/building, manual save/load and arrow-key/right-button scrolling on the development console; [626](../outputs/rct626/REPORT.md) confirms the later interactive session and cleanup | Window-edge scrolling stays still; fullscreen unqualified; sound deferred; no Xbox game FPS measurement |
| Software D3D7 | Scoped offscreen and windowed RGB-renderer samples pass through combined scenes; sustained synthetic scene has Xbox clock checks | Exact ideal alpha endpoints remain failed; perspective interpolation has PC results only; synthetic timings are not game FPS |
| Native GPU acceleration | No accelerated driver installed | Game rendering, a module name or software sample success is not NV2A acceleration |
| Other Xbox revisions | A user-supplied [1.6 schema-2 inventory](../outputs/inventory630/REPORT.md) validated | Encoder remains unidentified by this tool; no Windows qualification; further unit testing is deferred |
| Packaging | Hardware-info utility and private prepared E/720p Windows ZIP recipes and [delivery587](../outputs/delivery587/README.md) | RCT excluded; private Windows assets are not public downloads; clean physical provisioning remains incomplete |
| Installation/storage | Component builds and scoped prepared-image/emulator restore checks pass | Six clean-media FATX long-name exclusions, crypto failures and strict event failures remain; selected-file audits are not whole-volume health checks |

## Current engineering boundary

[PC628](../outputs/rct628/REPORT.md) measured a verified paused park for about
20 seconds and identified one captured `timeGetTime` caller. It does not establish
Xbox costs, game FPS, a polling fix or a native acceleration result. The bounded
physical game-cost comparison remains outstanding. Compatibility work on other
revisions is intended before acceleration, but physical testing of those units
is deferred in this conversation.

The latest diagnostic work is [678's host-only full-firmware timer integration](../outputs/timer678/REPORT.md).
It compiled a private XBE and passed 25 isolated full-image function fixtures;
there was no console launch or installed change. It preserves the existing
capture and encoded packet, then runs the bounded timer probe and halts without
calling the sender. Timer and SMC behavior are unchanged. The prior physical 674
capture received no UDP datagrams; the user saw lights off on a black screen and
then manually reset the console. Those observations do not identify a timer,
SMC or network root cause. A watched physical timer-only test remains next;
it expects no UDP and requires a power-cycle after its held indication.

The ordinary 720p configuration remains the baseline. 1080i is tabled, Ftdisk49
and shutdown-popup limitations remain recorded, and closed test identities must
not be rerun. Historical `outputs/` records and old bundle instructions describe
their frozen packages; use the maintained guides above for new work.
