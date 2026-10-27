# Current status and guide map

Reviewed October 27, 2026 through native CR19 test/restore diagnostic714; the retained480p handoff is703 and the larger720p pre-transaction checkpoint is710.
This page summarizes supported observations; individual reports retain their
original failures and scope. For the exact active attempt and next engineering
step, read [CONTINUATION](../outputs/engineering-notes/CONTINUATION.md) and
[STATUS](../outputs/engineering-notes/STATUS.md).

The incoming1.6 now has a watched kernel640x480p display retained through the
checked native handoff ([703](../outputs/native-gpu703/REPORT.md)). Native clock
and CRTC observations match kernel preparation; stride2560 is fully decoded.
Its clock selection equals the earlier720p snapshot, while output control differs.
One PFB photo bit is unknown due to glare. This is not native mode initialization
or Windows1.6 qualification. The [704 integrated transaction](../outputs/xcal-transaction704/REPORT.md)
passes880 linked model cases,32770 allocation boundaries and12 relocated cases.
The [705 larger bridge](../outputs/native-bridge705/REPORT.md) passes 12 diskless CPU
fixtures and 30 bridge/transaction model cases. [706 kernel preflight](../outputs/native-preflight706/REPORT.md)
passes the larger allocation, eight alias mappings, copy checks and cleanup.
The [707 watched repeat](../outputs/native-preflight707/REPORT.md) confirms a green
result and automatic return, with identical PCI/CRTC/sequencer observations.
PCI/VGA baseline values are captured; the functional native launcher and watched
mode-initialization test remain.
Host models do not qualify scanout, external clocks or Windows on1.6.
The [708 integrated native-mode experiment](../outputs/native-mode708/REPORT.md)
passed its host checks, but produced black output. The [709 watched repeat](../outputs/native-mode709/REPORT.md)
showed the initial blue kernel picture followed by black. Preparation records
match, but the native failure phase remains unknown; neither run qualifies the
mode change. Both were manually reset and collected. The [710 pre-transaction checkpoint](../outputs/native-mode710/REPORT.md) passed
fresh host checks and visibly held CYAN after native handoff/PCI/timer admission.
It was manually reset and collected; preparation state matches709. It intentionally
stops before video programming, so it cannot qualify a mode change or identify
the exact failure in708/709. The [711 baseline-only call](../outputs/native-mode711/REPORT.md) passed fresh
host checks and produced the reported GREEN held checkpoint before blanking.
It was manually reset and collected; preparation state matches710. This qualifies
only the baseline call on that run. Native mode initialization remains unproved;
the [712 paired blank/restore test](../outputs/native-mode712/REPORT.md) has a
reported black interval followed by the restored picture and GREEN hold. Its
manual-reset collection and audits passed, with the same preparation state as711.
Encoder/geometry programming remains unqualified. Next isolate the extended-register
unlock/check after blanking, while preserving the observed restoration path.
The [713 unlock/CR11 checkpoint](../outputs/native-mode713/REPORT.md) passed fresh
host checks and held GREEN after the unlock-key request, exact CR11 check and
restoration. Manual reset and nine-file collection/audit are complete; preparation
state matches712. This does not prove extended-register write access or native
mode initialization. Next isolate common setup with changed-register readback.
The [714 CR19 test/restore checkpoint](../outputs/native-mode714/REPORT.md) passed
fresh host checks and produced a user-reported GREEN held result. Manual reset,
nine-file collection and audit passed; preparation matches713. This supports one
temporary pitch-register write/readback and restoration, not the full mode change.
Next capture remaining common-setup register values before further write tests.

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
| Other Xbox revisions | User-identified1.6: kernel composite480i/HDMI720p baselines pass; minimal checked native handoff and [four-byte encoder read697](../outputs/native-xcal697/REPORT.md) observed | Native mode initialization and Windows remain unqualified. [699 timer observation](../outputs/native-timer699/REPORT.md) passed; [701 GPU snapshot](../outputs/native-gpu701/REPORT.md) captured native values matching the six shared GPU registers and four CRTC bytes in the pre-transfer snapshot;689 full-startup failure phase remains unknown; this unit's GPU field differs from inventory630 |
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
and its staged files matched. Later694-697 added independent display checkpoints
and native read evidence;689 itself remains inconclusive and closed.

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
fixed the ordinary boot path or qualified Windows1.6. Later694 qualified a
separate minimal transition; that is not a fix to the original full startup.

[694-697](../outputs/native-xcal697/REPORT.md) now provide physical evidence of a
checked minimal native handoff, framebuffer writes, PCI/status and bounded cable
and encoder reads.697's photo shows raw word2, block length4, completion10 and
final status0. All are closed after manual recovery and verified collection.
They preserve kernel-established scanout; native mode initialization is unproven.

[698](../outputs/xcal-protocol698/REPORT.md) explains the byte-versus-block length
inference and adds stricter host-active/abort/final-status handling in an isolated
host prototype.458766 modeled cases pass; no maintained driver change. The next
[699 timer-only probe](../outputs/native-timer699/REPORT.md) is built, validated and
launched once after watch/reset confirmation; its observation is pending. It has no native SMBus/encoder writes,
Windows payload or startup hook. Its failed first build/page check are preserved.
