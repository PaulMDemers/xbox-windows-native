# Current: diagnostic boot and normal restart verified; cause remains unresolved

462 reached the Windows desktop and returned through a normal restart, supported
by fresh startup/shutdown logs and five clean registry hives. Its preparation
record matches both the earlier failed460 and successful461 in every nonidentity
word. No first-refusal file was present. This is a successful diagnostic run,
not a demonstrated fix for intermittent boots.

All original720p boot files and startup remain unchanged. Ftdisk49 and Srv2013
remain recorded failures; the latter names WindowsF (historically dashboardC,
which was not accessed). No D3D workload ran. The next step is source review of
a bounded marker at early Cromwell entry; no hardware test is queued. All owned
processes are closed. See [462 closeout](../boot-refusal462/REPORT.md).

# Current: first-refusal diagnostic launched; screen observation pending

The new462 diagnostic records the exact first deliberate wrapper refusal after
logging, using a separate file and preserving the original status before cleanup.
55 host cases and independent decoder negatives passed before one console launch.
The original launcher, normal startup and720p settings remain unchanged.

Dashboard FTP has not returned within the observation window. The user's screen
report is pending; this alone does not establish a failed boot. No further launch
is queued. Collect once after dashboard return and review any actual refusal
record before deciding the next change. Details: [462 report](../boot-refusal462/REPORT.md).

# Current: successful boot/restart verified; failure boundary still unresolved

The watched461 diagnostic reached Windows and returned through a normal restart.
Cold logs confirm startup and shutdown; five registry hives passed validation.
Original720p boot files, drivers and startup remain unchanged. Ftdisk49 persists.
No D3D workload ran in this attempt.

Its complete preparation record matches the failed460 run in every nonidentity
word. The next diagnostic should capture deliberate wrapper refusals after
logging and distinguish them from later boot failure. This is not a proven fix
or evidence that allocation addresses explain the behavior. Both outcomes are
preserved in the [461 report](../boot-handoff461/REPORT.md). All owned processes
are closed and no further test is queued.

# Current: watched diagnostic reached Windows; cold collection pending

The user-requested fresh461 diagnostic reached the Windows desktop. Its logic
matches460; only the fresh identity/report path differs. This successful boot
and the earlier black/dashboard outcome are both preserved. It is not a boot fix
or D3D qualification. Normal Windows restart has been requested before collecting
the report, registry hives and event logs. No further launch is queued.

# Current: boot preparation verified; handoff investigation continues

The normal cold-start attempt also returned to the dashboard. Its registry and
logs were unchanged. A [separate instrumented launcher](../boot-handoff460/REPORT.md)
then verified the allocations, complete payload copy, both loader copies and
jump targets on the console. The installed launcher, drivers and720p settings
remain unchanged; no test startup hook is installed.

This narrows that diagnostic attempt to the remaining file-close/recheck/handoff
boundary. It does not prove paging changed or identify the cause. The console
returned to dashboard FTP with a complete report and unchanged Windows hives/events.
The user's visual report is pending; all owned processes are closed and no retry
is queued. Further instrumentation must distinguish the remaining boundaries.

PC D3D7 enumeration and earlier Xbox sprite/lifecycle passes remain separate.
Physical D3D rendering and games are still pending.

# Current: early returns through both launch routes; normal cold boot requested

The watched457 FTP launch and458 direct File Explorer launch both returned
without test receipts. Five registry hives and both event logs remained unchanged;
neither establishes D3D probe execution. Both test hooks are removed and all owned
processes are closed. The [direct-launch record](../d3d-direct458/REPORT.md) rules
out an explanation confined to FTP, while the actual failing stage remains unknown.

[Read-only459 verification](../boot-baseline459/REPORT.md) matches the known
working boot files/configuration/startup and validates the launcher section digest.
The user has been asked for one normal direct boot after full power-off, without
a graphics test hook. No host launch or automatic restart is scheduled. Await
that observation before changing the boot chain or scheduling another sample.

The earlier sprite/lifecycle passes and PC D3D7 software-device inventory remain
valid within their scopes. Physical D3D drawing and game compatibility are pending.

# Current: Direct3D device inventory passes on NT5 PC; Xbox comparison pending

The [new D3D7 discovery sample](../d3d-discovery455/REPORT.md) found Microsoft's
RGB software renderer through both default and explicit HEL paths. Its complete
descriptors and566 negative mutations passed independent checks. This establishes
capability enumeration only; no D3D device creation or drawing is qualified.

The [Xbox456 attempt](../d3d-xbox456/REPORT.md) returned without a probe receipt.
Five hives and both event logs are unchanged, so the failing boot stage remains
unknown. Its startup hook is removed and all owned processes are closed. A
[fresh457 package](../d3d-retry457/REPORT.md) is ready locally, awaiting the user
to watch one boot. It has not been uploaded or launched.720p is unchanged.

The earlier full sprite and bounded lifecycle controls pass on PC and Xbox.
Ftdisk49 and shutdown-time rundll32 popups remain separate system limitations.
Games, actual lost-surface restoration, D3D rendering and GPU acceleration remain
unqualified. All failures and historical untracked files are preserved.

# Current: bounded lifecycle controls pass on PC and Xbox

The [new lifecycle sample](../lifecycle-xbox454/REPORT.md) passed on both platforms:
64 measured iterations per backend,12,582,912 exact bytes per platform, repeated
surface release, owned-window focus checks and a fixed commitment-growth budget.
Both controls restarted normally. The Xbox hook is removed and all owned sessions
are closed. Ftdisk49 and two shutdown-time rundll32 popups remain separate limits.
Actual lost-surface recovery, GPU acceleration and games are not yet qualified.
Next is the installed Direct3D7 device/capability inventory; its design is ready.

# Current: complete Xbox sprite matrix passes

The [452 physical retry](../sprites-retry452/REPORT.md) passes all six palette,
format, keyed/clipped and overlapping-copy cases:174,080 independently checked
bytes and2,520 rejected mutations. It restarted normally, and the test hook is
removed. All owned processes are closed;720p/runtime/driver are unchanged.
Ftdisk49 and one shutdown-time rundll32 popup remain separate system limitations.
Next: surface lifecycle05, then legacy D3D device discovery. No GPU or game claim.

# Current: two user-confirmed direct boots; fresh sprite package ready

The user reports successful second and third direct boots with restart to the
dashboard; the first attempt is uncertain. These boots had no test hook. The
[fresh452 package](../sprites-retry452/REPORT.md) is built and checked locally.
Dashboard FTP timed out before login, so nothing was uploaded or launched.
Connectivity confirmation is pending; all owned processes are closed. Full
physical sprite qualification remains pending, followed by lifecycle and D3D
discovery samples. The unchanged720p baseline was not modified.

# Current: complete PC sprite matrix passes; Xbox launch comparison needed

The [450 PC control](../sprites-depth450/REPORT.md) passes all six sprite cases:
174,080 exact bytes across palette changes, keyed/clipped copies and overlapping
copies. The actual24-bit mode was verified and the original mode restored before
normal shutdown. The sample and pixel expectations are unchanged.

The [451 Xbox attempt](../sprites-xbox451/REPORT.md) returned without a result
directory. Its test hook is removed; five hives and both logs are unchanged, with
normal720p startup/launcher verified. A direct File Explorer launch comparison is
requested. No test remains queued. All owned sessions are closed. The earlier449
focused key-probe pass remains valid; full physical sprites/D3D remain pending.

# Current: Xbox RGB32 color-key diagnostic passes

The watched [449 retry](../key-retry449/REPORT.md) booted to the desktop and
restarted normally. Default and HEL each passed all12 stages at1280×720×32;
92,160 captured bytes matched with zero errors. The independent checker rejected
19,592 altered results. The same executable passes at24-bit on the PC control
and fails keyed copies at16-bit; no driver, DLL or expected pixels changed.

The test hook is removed and the720p baseline verified. Strict system qualification
remains false: Ftdisk49 and one shutdown-time rundll32 popup are retained. All owned
processes are closed. Next complete the full rung04 sprite/overlap matrix, then
surface lifecycle and D3D discovery. No native GPU or game support is claimed.

# Current: Xbox key diagnostic launch produced no receipt

One launch was accepted, but dashboard FTP returned without a result directory.
The temporary startup hook is disabled; the normal launcher and720p baseline
verified unchanged. Five hives and both event logs are byte-identical. The screen
observation is pending; no Windows entry or sample execution is proved.
[448 evidence](../key-xbox448/REPORT.md). The PC24-bit pass remains valid; the Xbox
RGB32 probe and complete rung04 matrix remain unqualified. All owned processes
are closed. No driver or display changes were made.

# Current: RGB32 key diagnostic passes at24-bit; Xbox package ready

The identical diagnostic that failed on the16-bit PC desktop passes all12
operations on both backends at24-bit:92,160 exact bytes. Mode restoration and
normal restart are verified. [447 evidence](../key-depth447/REPORT.md).

This supports desktop-depth dependence; no runtime/driver patch was made.
The [448 Xbox package](../key-xbox448/REPORT.md) is compiled and checked for the
existing720p/32-bit baseline. Dashboard FTP timed out before authentication,
so nothing was uploaded or launched. Awaiting console readiness.

Fullrung04 laterRGB32 sprite stages, lifecycle tests andD3D remain next; no new
game, acceleration or whole-system qualification. Previous failures retained.

# Current: RGB32 color-key behavior isolated on the NT5 PC control

The new [diagnostic446](../key-semantics446/REPORT.md) passes all plain RGB32
copies and reproduces keyed-copy failures with three keys, with and without
clipping. Full key values are retained. All captured pixels fit a low16-bit
comparison model; the responsible implementation is not traced. Both default
and HEL completed all12 operations and correctly reported failure.

92,160 captured bytes;11,416 evidence mutations rejected. Normal restart, clean
cold audit, independent20-file readback and145 archived dependencies. The new
launcher enforces completed preflight itself;59 host refusal checks passed.
No Xbox changes. Next compare the same binary on an actually enumerated24-bit
desktop, then qualify the Xbox path before lifecycle and D3D discovery.

# Current: palette/RGB565 sprites pass on NT5; RGB32 key issue isolated

Rung04 now builds and has documented run/check commands. Four default/HEL
indexed8 and RGB565 cases pass 118,784 independent bytes, including palette
updates, color keys, clipping and overlapping copies. RGB32 omits pure-red
pixels on the 16-bit PC desktop; the behavior follows color, not clip edges.
The actual faulty component remains unresolved. A 32-bit desktop probe was
refused by the pinned Cirrus driver before any sample ran.

[444 results](../sprites444/REPORT.md), [445 refusal](../sprites445/REPORT.md).
All three new PC guests restarted normally, are cold-audited and closed. Earlier
failures and one host preflight-ordering error are retained. Xbox unchanged;
no rung04 physical qualification, D3D or acceleration claim. Next establish a
suitable NT5 mode control and narrow the 32-bit key comparison before hardware.

# Current: windowed DirectDraw presentation passes on NT5 and Xbox

Rung03 default/HEL covers visible, covered, moved and uncovered windows with
exact clip regions and unchanged neighboring GDI content. Each platform checks
3,604,480 bytes and rejects468 evidence mutations. Source/build/run/check
instructions are in docs/graphics-samples.md. Driver and720p mode unchanged.

[440 PC](../presentation440/REPORT.md) and [442 Xbox](../presentation442/REPORT.md)
are closed with normal restarts. The Xbox test hook is removed. The firstPC
stacking-order test failure439 and zero-write staging refusal441 are preserved.

Strict system qualification remains false: Ftdisk49 and two shutdown-time
rundll32 initialization popups recurred. No D3D, acceleration, performance or
physical scanout claim. Next is palettes/formats/color-key sprites, followed by
surface lifecycle and the D3D discovery/triangle rungs. Original games untested.

# Current: graphics ladder passed scoped NT5 and Xbox controls

Six allowed cases now pass on both the isolated Windows 2000 PC and installed
Xbox at unchanged 720p. Each verified 129,024 source/destination bytes and
rejected 402 actual-evidence mutations. Both restarted normally. Physical438's
temporary hook is removed; protected code and startup are unchanged. See
[437 PC](../graphics-nt5437/REPORT.md), [438 Xbox](../graphics-xbox438/REPORT.md).

Physical strict qualification remains false: existing Ftdisk49 and two rundll32
initialization popups during shutdown remain recorded. Their initiating process
was not traced. Five hives have clean headers and raw-value agreement; inherited
unknown typed DRM data and missing full allocation audit remain limitations.
No new display driver, primary-surface presentation, D3D or acceleration claim.

Next: rung03 primary surface/window clipper/GDI coexistence, with a fresh PC
control before a distinct Xbox attempt. Do not rerun437pc001 or438physical001.
All owned processes are closed, no test queued, and1080i remains paused.

# Prior: runnable graphics ladder foundation

[Samples 00–02](../../docs/graphics-samples.md) implement a GDI pixel reference,
DirectDraw capability inventory and system-memory copies. The current build
passed six allowed modern-Windows host cases and independent pixel checks;
NT5/Xbox execution remains pending. A hardware-only system-memory attempt
crashed on the host; its evidence is retained and that combination is explicitly
refused in the current sample. Hardware-only inventory remains available.

The ladder continues through presentation, palettes, sprites, lifecycle and D3D
rendering toward the game goals. Those later rungs are planned. No console,
driver or display-mode changes; 1080i remains paused. See [436](../graphics-ladder436/REPORT.md).

# Current: clearer build-to-boot documentation; classic games are the next milestone

The [new walkthrough](../../docs/build-to-boot.md) connects component builds to
Windows setup, offline conversion, package layout, FTP readback and first boot.
It explicitly identifies the missing portable conversion and six unresolved
FATX paths; this is documentation, not a newly qualified clean installer.

The [graphics roadmap](../../docs/graphics-roadmap.md) targets the original
RollerCoaster Tycoon and The Sims, beginning with exact versions and API probes.
Neither game nor native Direct3D is qualified. The current display driver declines
DirectDraw, so surface/GDI coherence must be designed before exposing it. Native
GPU acceleration has separate ownership/synchronization requirements. No new
build, console access or driver change occurred. 720p stays the working baseline,
and the 1080i investigation remains paused.

# Current: 1080i investigation paused; ready to pivot

The findings, evidence limits and resume criteria are consolidated in the
[1080i handoff](../../docs/1080i-investigation.md). The issue remains unresolved:
normal PBKit initialization did not restore lost row detail.720p remains the
working default. All display tests are closed, no new test is queued, and the
user has requested a pivot to new tasks. Historical status entries follow.

# Current: PBKit initialization does not fix 1080i detail loss

The watched comparison and four photographs show the same parity-dependent
solid-color regions before and after normalPBKit initialization. Correct CPU
pixels and address-mode3->2 did not restore the displayed thin stripes. The
remaining investigation is actual scanout/field handling; the responsible stage
is still unproved.720p remains the supported working baseline, no test queued.
See [visual result](../pbkit-compare435/VISUAL002.md).

# Current: PBKit comparison completed; visual confirmation pending

The same1080i framebuffer was captured before and after normalPBKit initialization.
All2,097,152 checked pixels are exact; among captured registers only the address
mode changed3->2. This does not prove a fix. We are awaiting the user's orange-
versus-cyan observation. The console returned to the dashboard, all sessions are
closed, and the installed720p Windows baseline remains unchanged.
See [comparison evidence](../pbkit-compare435/REPORT.md).

# Current: live raster timing captured; 1080i row loss unresolved

A new read-only hardware probe completed and returned to the dashboard. Its
41,071 samples show the expected 540-line CRTC active area for 1080i and about
60 cycles per second. Pitch is correct; standard double-scan and vertical-scale
controls are off. This narrows the software investigation but does not establish
that opposite source rows are fetched for alternate fields. No adapter fault or
fix is proved. Next review the normal graphics initialization's scanout setup
before a controlled comparison. Windows remains at the known-good720p default.
See [live timing evidence](../field-timing434/REPORT.md).

# Current: second display reproduces the 1080i artifact

A fresh comparison on the user's new display reports the same visible behavior.
All captured pixels and read-only timing checks pass; old and new runs have the
same captured stock timing values. This makes a TCL-only explanation less likely,
without identifying the shared adapter or Xbox output as the cause. Adapter/new
display identification and actual incoming signal format are pending. Windows
remains720p, baseline unchanged, all sessions closed and no next test queued.
See [new display comparison](../display-compare432/REPORT.md).

# Current: photographs show row-parity-dependent loss of fine detail

Windows test photos show single-line stripes collapsing to solidblack/magenta
or white/green while two-line stripes remain. This matches selecting alternate
source rows, consistent with field-based processing. Still photos do not prove
permanent field loss or identify the responsible device. The user reports the
same effect with the stock Xbox test and confirms a direct adapter-to-TV path.
The corrected live report adds green/purple alternation and black/white flashing
during movement, so camera sampling alone cannot explain the symptom. Odd-row
movement of the unchanged pattern explains the parity-color swaps under a model;
the actual processing algorithm and field order remain unmeasured.
Next is identifying that equipment and changing one output-chain variable in a
controlled comparison. No new hardware operation;720p remains the Windows default.
See [photo interpretation](../field-photos431/REPORT.md).

# Prior: 1080i issue also observed outside Windows

The Windows pattern tests at720p/1080i both returned exact pixels and zero
shadow-to-mapped-framebuffer mismatches, including after movement. The stock
Xbox video API comparison also returned exact pixels; the user reported perfect
720p and solid alternate bands at1080i. Fourteen stock timing registers per mode
match our public profile constants. This points toward the shared interlaced
output path, without yet identifying encoder, adapter, TV or lost-field behavior.
Photographs and a targeted output-chain comparison are next. Windows stays720p;
no speculative driver patch or1080i promotion. All trials are closed and no
hardware test is queued. See [428](../field-scanout428/REPORT.md) and
[430](../stock-field430/REPORT.md). Windows runs retain sole newFtdisk49 failure.

The clean-install prototype now discovers a real contiguous NTFS image inside
FATX, reproduces all32MiB exactly and independently reads a69-character filename.
Fifty host cases pass. It is still a read-only host prototype, not a bootable
Windows solution or resolved install/restore gate. See
[429](../image-discovery429/REPORT.md). No release tag or public Windows bundle
is qualified by these results.

# Prior: contiguous image boot route reviewed

427 narrows the first image prototype to a contiguous FATX file. The existing
loader/HAL partition path could expose its inner NTFS range as Windows' system
partition, avoiding a new file-backed disk driver. The parent FATX E range would
be absent from ordinary Windows partition enumeration. This remains uninstalled
and does not prove exclusion against raw disk access.

Eleven full loader/HAL source files and the owned kernel's relevant static
callsites were reviewed. A host projection/read-only adapter passed4,952 checks.
No native code, guest or physical console changed. Next is actual read-only
FATX image discovery and loader projection before any writable boot. See
[427 report](../image-handoff427/REPORT.md).

The720p demo remains available. All owned commands are closed; no hardware test
is queued. Long-name storage, clean install/restore and release gates remain open.

# Prior: fixed image storage prototype selected

426 selects a fixed NTFS image stored on FATX for further development. The
comparison covers the existing namespace, boot, dashboard and recovery paths.
A host-only mapping/lifecycle model passes4,065 synthetic checks, including
fragmented/high-LBA requests, guard contents, stale allocation, incomplete
descriptor publication and failed writes/flushes. See
[426 report](../image-volume426/REPORT.md).

This is not yet a driver or bootable image solution. Next is proving early
Windows block-device/ARC initialization and exclusive backing allocation
ownership, then a read-only prototype. Paging, dump support, real durability and
install/restore remain required. No hardware change or guest launch occurred;
the720p demo remains available. All owned sessions are closed.

Six clean-transfer exclusions and strict events remain failures. No public
Windows bundle or release tag is qualified by this host model.

# Prior: failing security-storage requests identified

425 completed one fresh emulator debugger run and cold audit. It observed
STATUS_NAME_TOO_LONG for a44-byte userSID directory under Crypto/RSA, a69-byte
machine RSA key filename, and a services.exe request for the44-byte user Protect
SID directory during userDPAPI. All145 observed file calls paired with returns;
seven native checkpoints and full debugger cleanup passed. Service RPC identity
was not independently traced. See [425 report](../crypto-path425/REPORT.md).

Normal restart, orderly exit0, clean FATX allocation, five clean hives and3149
unchanged protected Windows binaries are recorded. Strict qualification remains
false for inherited Ftdisk49/kbdhid1; this debugger run is not ordinary validation.
No physical Xbox change or functional driver patch occurred. The720p demo remains
available. All owned processes are closed; no hardware test is queued.

Next is a compatible long-name storage design and bounded crash/collision models,
followed by driver integration and actual API/namespace/restore tests. Raising
FATX's fixed42-byte directory field limit is not a fix. Six clean-transfer
exclusions and public Windows-bundle gates remain unresolved.

# Prior: clean-install security storage blocker confirmed

The 423/424 emulator comparison is complete and all owned processes are closed.
The same original NT5 probe passes user/machine RSA key and DPAPI persistence on
NTFS. On FATX, user RSA/user DPAPI creation return filename error206, machine RSA
creation fails, and only machine-scoped DPAPI passes both boots. Actual NTFS key
files have69byte components and a44byte userSID directory. The exact failing
native file request remains untraced; no namespace repair has been implemented.

Both FATX boots completed normal restart and orderly host exit0. Full E allocation
is clean, five hives agree in independent raw values and3149 protected binaries
are unchanged. Ftdisk49/kbdhid1 remain, so strict qualification isFALSE.
402actual-log negative controls reject malformed evidence; source/binary/frozen
inputs and independentNTFSselectedfiles were rehashed. See
[424 report](../crypto-fatx424/REPORT.md) and [423 control](../crypto-persistence423/REPORT.md).

The physical720p demo is unchanged and usable; no physical test isqueued.
Six FATX transfer exclusions, COM+, clean installation/restore and1080i remain
open. Next work is a bounded real file-request trace, not another identical
probe-only run. Public install/release docs now state the measured limitation.
All failures and private recovery material remain preserved; no release tag.

# 422 CLOSED: rebuilt loaders booted; original demo restored

User: "it booted and worked fine, it has rebooted to the dashboard". This is a
successful user-reported boot/use under the requested File Explorer protocol;
individual Xromwell transitions and media playback details were not separately
reported. The exact observation is preserved in user-observation001.json.

restore001 completed2026-10-16T23:55:09.634269UTC. Allthree original loader files
restored and selected code/startup hashes verified. Independent read-only
rollback-verification001 confirms originals exact, .422used candidate files exact,
.old/.new paths absent, and saved events/startup byte-identical on repeated read.
No consoleC access, relaunch or Windows-setting change. No rollback reboot claimed.

Event scan: system525->530records, application5->5; allprior decoded records
preserved, no duplicate record numbers, new records526..530. One EventLog6005
startup and6006normalshutdown,6009version,Tcpip4201, and sole warning/errorFtdisk49.
The preceding log already held85Ftdisk49 records. This is a new instance of the
known error, NOT error-free qualification. Record-scan/ring/message-render limits
remain explicit. Rawlogs/private decoded records kept underE:/xwn422.

Scoped reconstruction boot/use/shutdown evidence and byte-level rollback PASS.
Strictclean-event/clean-install qualification remainsFALSE. This test changes only
three metadata-different reconstructed loader artifacts on the existing Windows
installation. It does not validate fresh403/406 assembly, otherXbox revisions,
FTP/menu launch parity,1080i, or whole-install restore. No public release tag.
Candidate is now INACTIVE; preserved416stage and422used files are evidence only.

All owned processes closed. Do not relaunch/recollect422 or call either416/422
activation/restore again. Preserve original pending reports underprior-status001;
prepared-review input hashes remain verifiable there. Earlierfailedpreflight and
runtime-state hive review remain unchanged. Next work: clean-media FATX path
exclusions/provisioning and disposable install/restore qualification, then matched
physical fresh-install test. Corrected421utilitybundle remains available and other
revisions awaitinventory.1080i field/scanout discriminator remains separate.

# 422 reconstructed loader candidate ACTIVE; manual result pending

Read outputs/loader-physical422/REPORT.md,NEXT.md and activation001.json.
Activation completed2026-10-16T23:49:18.279830UTC, allthree416candidate files at
original E:/Applications/XWNEBoot paths exact; original active binaries preserved
as .422old, plus inactive staged rollback. XBE/INI/Windowsdrivers/startup/current
hives unchanged. No consoleC access. No launch command sent, no observer running.
User asked ONE FileExplorer launch E:\Applications\XWNEBoot\default.xbe, report
Xromwell/Windows, play C:\xwndemo407\play.cmd, then normal Windows Restart.
No test/commandwindow expected. Do NOT send FTPlaunch or repeat activation.

Old416 hive hashes differed:422preflight001 refused beforewrites. Separatecapture
and complete decoded key/value comparison:6022SYSTEM/26921SOFTWAREkeys,24+8value
changes onlyruntime state (logon/shutdown/DHCP/serverGUID/RNG/WBEM/profile/sync).
Noadded/deletedkeys/types; allotherdecodeddata includingdrivers/display/pagefile/
mounts exact.128negative reviewmutations rejected. Originalfailure/stage untouched;
new422pins CURRENT hives explicitly. Privatehives/events E:/xwn422/before001;
actualpreactivationevents/startup E:/xwn422/activation-before001.

On user's dashboard return: run outputs/loader-physical422/activate.py restore
ONCE with authorizedFTPenv. NOT416script. It captures afterevents/startup, journals
known-byte renames, retains candidates as .422used and rechecks selected originals.
Never retryunknown/partialstate; inspectjournal. Restoreplanner identicalAST416,
256states14accept242refuse; no physicalrestore yet. Afterward analyzeeventdelta
with actualpreactivation boundaries, preservewarnings/errors andringdecoderlimits,
recorduserobservation separately, updatepublicreadinessandnotes. No cleaninstall/
strictorotherhardwarePASSyet. Both candidate andoriginal exist; no fullOSreplace.
Allownedhostsubprocessesclosed. 421utilitysuccess/bundle and1080i question remain
separate; same720p mode retained. Hardware FileExplorer route needed to avoid
changing the route while comparing loaders. All closed420/421 records preserved.

# 421 physical inventory fixed; corrected tester kit ready

420 is CLOSED failed after the user reported black screen/manual restart.
physical-collection001 preserved 28 records/896 bytes; last pending PCI query is
0:0:1 (stage20,arg32). Pinned ReactOS explicitly documents that query hangs Xbox.
No old attempt rerun/recollection. Original raw trace and utilities unchanged.

421 corrected ordinary scanner omits0:0:1/.2 and bus1 device aliases; schema2
records xbox-safe-v1. No tracing/Windows driver/loader/display change. Native
XBE f9163c73c3baa556c80138e122dbc81fe9aec77bd7ec3d951ec9fd9ad0778d5d,
110592 bytes, pinned nxdk58427c/prebuilt libraries unchanged.524 actual-header
ASan/UBSan checks;5 validator tests each Windows/Linux;9 bundle tests pass/1 skip.
Fresh unused blank8GiB emulator C:/xwn421/emu001 CLOSED exit0/nofallback. Valid
report, clean E3dirs1file4clusters0errors/orphans; QCOW/EEPROMpass. Reserved1540
change retains strict whole-disk FALSE. No backing chains moved; E margin tight.

One authorized FTP launch of E:/Applications/XWNInfo421/default.xbe accepted
23:18:36UTC; dashboardFTP/newreport observed23:19:19, collected23:19:27. Complete
5353-byte schema2 report exact twice, SHA0cfa10dd4caf622d7a5c72611d2860977ec781d1d1016cf19f7d0caa1256fa2c.
Kernel1.0.4034.1,64MiB,Conexant response; raw PCI function aliases remain and are
NOT independent devices. Selected Windows files/oldutility/420trace unchanged.
No consoleC access, no Windows boot/full physical disk audit/other revision claim.
All owned sessions CLOSED, no xemu processes found in closeout query.

Corrected utilities archive E:/xwn421/xwn-utilities-preview-421.zip,
7208064 bytes, SHA24a52f961bddd1911dcf7003a606b8b5c997ebd90a0c275a3a21d2e0c942011d.
2247 files/324dirs verified against staging; matching source/header, SDK notices,
updated host validator/docs. No Windows/media/firmware/keys; NOT uploaded as a
release asset. Public docs warn against old417/417b. Other configurations need
coordinated inventory tests; manifest remains experimental-not-hardware-qualified.

Next: deliver corrected utility bundle, then resume distinct416 matched boot-chain
comparison and clean install FATX/provisioning/restore gates;416 remains inactive.
720p demo untouched.1080i is plausible mode-path discriminator, not proved cause;
see420INTERLACE.md for odd/even rows + actual scanout readback comparison. No1080
experiment done. Do not duplicate420/421 launches or collection. Keep historical
failures/private recovery/physical rollbacks. Read421REPORT/final-review/actualrecords.

# 417 public tester kit built; hardware deferred to this evening

User requested public-repo readiness and external-tester bundles. No physical
FTP/read/write/launch occurred. 416 remains staged INACTIVE; no activation record.
The existing E720p/FATX390/video303/audio004 demo and all rollbacks are unchanged.
Hardware work resumes only when the user is ready this evening.

New MIT src/utilities/hardware-report builds with pinned nxdk58427c prebuilt libs.
Build002 fixes E alias for DVD launches and verifies native Partition1 target;
no replacement of an existing mapping. Build001 compiled, emu001 produced no
report; failed cold audit/source preserved. Fresh emu002 cold-read exact1470-byte
report:12 PCI devices, kernel64MiB, Conexant response, E-space status. Full E
allocation3dirs1file4clusters0errors/orphans; QCOWchecks/EEPROM unchanged. Entire
disk equality still FALSE at reserved byte1540. No physical/multi-revision claim.
Owned xemu exited0 with no fallback; blank fixture has no dashboard-return proof.
No screenshot was captured. All owned subprocesses are CLOSED.

FINAL utility archive E:/xwn417/xwn-utilities-preview-417b.zip (7,206,072 bytes),
SHA256070b8c5b54669c6b88a3459e785705aae7cae70873eb61a76d3621f87525792a.
2246 files/324 dirs readback-verified; only binary is tested110592-byte XBE,
SHAdd7fb7777d1806e478571f2680db771ea0ec3d13acba0e679e9077fb420074c7.
Includes source/SDK notices, host inventory/bundle/FTP-readback validators and
short tester instructions. No Windows/firmware/EEPROM/private recovery data or
public binary upload. Earlier417 ZIP superseded by417b; retain originals.

New public docs/testers.md, tester-bundles.md, tester-report-template.md and
 tester-rollout.md explain inventory first, E-only matched720p, launcher-last
readback, direct UnleashX File Explorer, saves/audio/restart and removal limits.
README/licensing/release pages acknowledge PUBLIC repo; no intermittent-boot
cause claim. Added GitHub issue template/read-only pinned CI. Local46 Linux
host tests pass; Windows46 with10 platform skips. All8 source profiles unchanged.
Remote CI status is separate; inspect actual run before claiming completion.

History00124,532 reachable local blobs: no supported token/private-key/binary
patterns. Local paths/private IPs/emails retained. All176 credential matches in
174blobs triaged as env lookups, standarddefaults, boolean config or test text;
not comprehensive clearance. No history rewrite/visibility change/tag.

New tools/tester_bundle.py plans/builds/verifies deterministic ZIPs and exact
manual FTP readback including deferred launcher; it is NOT Windows provisioning,
private-data sanitization or rights clearance. Windows bundle NOT ready:6FATX
long-name exclusions, clean registry/provisioning, strict events and physical
install/restore remain. Do not distribute the private256/399 recovery captures.
Next evening: physical inventory XBE check, then existing416 controlled loader
comparison. In parallel continue clean Windows provisioning using owned media,
then a fresh matching E720p tester package and disposable install/restore check.

Capacity guard preserved; closed host executables and JSON/log evidence were
NTFS-compressed in place with every hash verified, no deletion/backing movement.
Prior launch capacity refusal and package path-lookup failure retained separately.
New xemu portable has immutable executable hardlink, own config/EEPROM/child/ports.
Exact details/failures under outputs/tester-readiness417/REPORT.md and JSONs.

# 416 candidate prepared/inactive: complete loader correspondence

User said proceed. New fresh HAL/loader builds used independent403 bootstrap
compiler8ab0685d with6587-entry receipt and unchanged profile source trees.
Canonical diagnostic source spelling AND root length gave HAL001/ROSloader001
complete-file matches except8 metadata bytes each. FreeLoader001 FAILED complete
correspondence:11395 differences, text virtual size32 shorter; preserved.
Actual generated version header/banner differed in date/revision/length.

Separate loader002 used original SOURCE_DATE_EPOCH and disabled CMake Git lookup
only for correspondence. Generated buildno.h byte-exact original02eaeacf...,
no source or post-link binary patch. HAL001/FreeLoader002/ROSloader002 now differ
from live415 only8/5/8 timestamp/checksum bytes. All other code/data/relocations
exact.77 actual mutation checks pass. Each build17 inherited warning instances,
zero new messages. This historical banner is NOT a new release identity.
docs/building.md now explains path/version differences and limited claims.

Stage001 completed one inactive upload/readback to Xbox E:/xwn416-stage:
three candidate files, three originals and owner marker. Host E:/xwn416 mirrors
candidate/baseline. Current active launcher/loaders/config/startup/SYSTEM/SOFTWARE
verified unchanged. No Xbox C access, guest launch, active-file change or public
tag. Source hard-codes XWNEBoot in BOTH Xromwell/FreeLoader; copying an XBE to
another folder would NOT test a separate chain. No default.xbe in stage folder.

User asked once if near console and ready to observe SAME File Explorer path;
answer pending at closeout. No activation yet. Read actual records before work.
Next on readiness: activate.py activate ONCE, then manual File Explorer launch
E:/Applications/XWNEBoot/default.xbe. Existing XBE/INI/Windows/startup unchanged;
only reviewed three loader files temporarily replaced with journaled renames.
Observe Xromwell->Windows, clip C:/xwndemo407/play.cmd, normal restart to dash.
Then activate.py restore ONCE captures events/startup and restores originals.
No FTP SITE launch substitute. Unknown bytes refuse;256 pure rollback-state
tests(14accepted242refused), no runtime FTP failure-injection claim. Pre/post
event captures do not themselves waive strict-event or full-disk requirements.

All owned build/stage/check commands closed; no xemu process observed. No new
emulator fixture or prior-runtime parenting. final-review pins33 records/15
private outputs; exact source/build logs, original partial comparison preserved.
No physical launch cause/intermittency established. Current E720p/FATX390/video303/
audio004 demo/F rollback unchanged. Six FATX long-name exclusions and strict
event/clean-registry/restore qualification still block public clean release.
C22538371072/E21591097344 bytes at post-stage check; retain20GiB projected guard,
no new build until capacity rechecked. No backing chains moved.

# 415 closed: working demo versus clean rebuild, no physical mutation

User approved comparing the working demo against the clean rebuild. This
supersedes the older next-step early-Cromwell tracing plan. Do not describe the
failure as intermittent: same-build/same-route/same-start-state randomness has
not been established. Successful direct File Explorer and failed menu/FTP
observations used the same installed demo files. Fresh403/405/406 binaries have
not been installed over that demo; no newer-binary physical regression proved.

415 one read-only FTP capture:31 E files, all protected411 code/startup exact.
34 files extracted from CLOSED406 disk, disk SHA unchanged and original cold
inventory exact.65 private captures rehashed,21 analysis/source inputs pinned.
No console C access, physical writes/launches, builds or guest experiments.
All owned commands closed; read-only process query found no xemu process.

Launcher differs only one displayed-date byte plus20 valid section digest bytes;
wrapper/Cromwell text exact. Six project drivers differ only timestamps/checksum.
16 selected Microsoft system/player files exact. HAL/FreeLoader/ROS loader have
nonmetadata differences: build-source strings explain SOME differences, not
complete equivalence. Linear FreeLoader disassembly includes data:2153 unknown
spans are not2153 proven instruction changes.74 actual binary mutation controls
pass, including digest-valid changed XBE code refusal. No runtime equivalence
or failure-cause claim. See baseline-compare415 REPORT/DESIGN/NEXT/final-review.

Selected registry comparison: fresh HidServ registration absent (exe/INF exist),
AutoReboot1 vs demo0, six ImagePath text-identical type differences; stored video
defaults differ but do not establish effective mode. Demo was observed720p.
Fresh freeldr.ini omits demo MinimalUI=Yes, and fresh lacks marker-gated outline
startup helper. No configuration automatically changed. libhivex loader failure
before hive open preserved; exact reader succeeded with process-local lib path.

Next resolve actual remaining loader build differences from pinned source and
compiler records, prepare separate candidate with matched configuration, then
use SAME direct File Explorer route/start-state for a physical comparison.
Do not substitute FTP SITE and call it the same route. Do not replace the whole
demo or waive six FATX long-name exclusions/strict-event clean-install blockers.
Demo path E:/Applications/XWNEBoot/default.xbe; clip C:/xwndemo407/play.cmd.
E720p/FATX390/video303/audio004 and F rollback unchanged, no public tag.
No hardware action queued. C24707448832/E21598044160 bytes at final read-only
capacity check; preserve projected20GiB guard and all backing chains.

# 413/414 closed: original Cromwell device initialization observed

User finished recording the demo and explicitly authorized console access again.
This supersedes the historical411 demo hold below. No physical access occurred
in413/414; E720p/FATX390/video303/audio004, F rollback and video are unchanged.
Direct launch remains E:/Applications/XWNEBoot/default.xbe via File Explorer;
Windows clip C:/xwndemo407/play.cmd. Physical menu/FTP failure is unexplained.

413 original PCI/video/backdrop returns and USB call reached at nine actual
instruction stops. Final HMP screendump was unsupported: original run FAILED,
source/report immutable. Separate completed-instruction review verifies17
captures/24 actual report mutations. No visible-screen claim for413.

414 accepted2026-10-16 02:04:50 UTC, closed02:05:41. Seven stops reached USB
and IDE returns then BootFromDevice call BEFORE execution. Original374 launcher
and288316-byte payload exact;11 source pins and217 frozen inputs. Two actual
mode/register-validated1280x720 software framebuffer captures show Xromwell and
isolated E FreeLoader message.25 memory captures/20 actual report mutations.
Generic emulator keyboard/mouse only, not physical Razer behavior. No Windows
boot/shutdown, ordinary timing, TV scanout or physical-failure reproduction.

Both new children use never-executed412 preparation002, not old runtime parents.
All breakpoints removed, physical mode0, orderly host exits0 without fallback;
all sessions closed and read-only process query found no xemu process. Never
relaunch/recollect/parent413 or414. Read their REPORT/DESIGN/NEXT/final-review.
Private E:/xwn413 and E:/xwn414. Shared source/SDK/binaries were not modified.

Both cold audits retain strict whole-disk FALSE55bytes: reserved1540,sector8,
three directory creation bytes; no writer attribution/waiver. Complete10GB
mapping and separate E6552 names/content hashes exact;275dirs,254dirclusters,
zero allocation errors/orphans, QCOW/EEPROM clean, seed unchanged. Raw private
namespace/frames remain on E; compact reports only in Git.203 frozen inputs413,
217 in414 exact.413 unsupported-command failure remains distinct from414 PASS.

Next inspect exact BootFromDevice FATX read/format/entry/error return paths for
one new bounded discriminator, not another early-init repetition. Physical use
is authorized but first inspect actual dashboard/state; no random boots or
speculative fix. Six genuine FATX long-name exclusions and strict-event failures
still block clean-install/public-release qualification. No public tag yet.
C26995597312/E21645754368 bytes free at closeout: preserve20GiB projected guard,
private roots/leases and backing chains. No new hardware test queued.

#411 DEMO READY /412 ORIGINAL HANDOFF TRACE CLOSED

User requested lastbootable+video available while work continues. 411 readonly
verification61files exact, no writes/hostlaunch/Caccess. User instructed to run
UnleashX FileExplorer E:/Applications/XWNEBoot/default.xbe, then Windows
C:/xwndemo407/play.cmd. Maynowbeusingconsole; doNOTinterrupt/deploy. Current
physical E720p/FATX390/video303/audio004 andFrollback unchanged. Frontmenu/FTP
issue remains; original407 windowedvideo/audio good, fullscreen drops retained.

412 exactoriginal374launcher emu001 accepted01:24:37UTC October16;6stops passed
through actual pagingdisable/CSfarjump/Cromwellentry02600000 by01:24:44. Original
loadedbytes/payload/copies exact; lowphysical00085000/loader02000000, CR0PGoff,
CR3zero. No guest memory/registerwrites, all12bpadd/removes paired, physicalmode0,
26privatecaptures rehashed/20actualmutationsreject. StopBEFOREfirstCromwell
instruction, thenhoststop/quitexit0; NOTordinary/physical/Windowsshutdownproof.
ActualIDT/kernelPEcaptured, notfullsymbolmatch. Allownedsessionsclosed.

Preparation001 refused differentfresh406launcher beforeguest; preparation002
newunusedchild replacesonly21bytes ofsameallocatedlauncher with exact374,
fullmap/local1703936bytecompare, parentsunchanged. Runtimechildfresh,191pins,
privateE:/xwn412. Neverrepeatclosed412or409/410. Read412REPORT/DESIGN/NEXT.
Cold10GBmap:55changedbytes(1540,sector8,3directorycreationbytes), strictdiskFALSE;
writerunknown. Separate E6552names/contenthashesexact,275dirs/254dirclusters,
0errors/orphans,QCOW/EEPROMclean, sourceunchanged. Originalauditfalsepreserved.
Rawnamespace-review privatecopy E:/xwn412/cold001, compactsummarycommitted.

Nextsource review/NEW boundedtrace of original earlyCromwell PCI/video init,
usingstaticleads onlyafterbyteverification; no guessedaddresses/randomrepeatboot
or speculativepatch. SixFATXlongpaths/strictevents/publicrelease remainopen.
Maintain20GiBguard;C/E tight. Userdemoandemulatorfixtureareseparate.

#410 CLOSED: hardware relocated-copy preparation PASS, handoff still unobserved

Read outputs/launch-handoff410 REPORT/DESIGN/NEXT/final-review and actual records.
One FTPlaunch01:06:47UTC October16; complete144byte report/dashboard01:07:10,
collection closed. Payload288316bytes and two1024byte loader copies exact;
both targets02000050, critical loader/GDTspan224. PayloadPA01f00000, loaderPA
02000000, lowVA02000000 backed by00086000. Distinct backing consistent with
original dual copies, not failure. All62protected files/diagnostic/owner exact.
No Windowsboot/Caccess/driver/Startup/originallauncherchanges. Historical407
cause stillunknown; paging/CR3/GDT/Cromwell entry NOT executed by410 probe.

Build002 d1b86685... compiled, exact original copy/fixup+loader source reviewed.
Host00221 actualx86 cases with modeled kernel/file semantics;225decodernegatives.
Build001/host001 diagnostic address-expression bug caught beforedeployment,
preserved; corrected reader uses explicit74byte index. No emulatorrun. All
source/hostpins rehashed, original407ninepins unchanged. Private E:/xwn410.
Allownedprocessesclosed; no testqueued. Neverrepeat410or409closedattempts.
Next bounded owned-emulator trace of original paging/handoff, using ORIGINAL
symbol offsets, actualkernel/code/register pins and freshunusedfixture. No
speculative allocation/copy patch. SixFATXlongpaths/strictevents/publicrelease
remainopen. Physicaldemo/rollbacks unchanged, fullallocation notaudited here.

#409 BOTH PHYSICAL PROBES CLOSED: identical allocation results

B user observation: "B - it launched to xbox logo, then black screen, then back
to the dashboard". Collected ONCE at 2026-10-16 00:58:54..00:59:02 UTC. This was
an intentionally returning diagnostic, not a Windows boot. manual-collection002
and pair-review002 record the complete80-byte result, identical to A except the
two attempt-cookie bytes. Both phases4; payloadPA01f00000, loaderPA02000000,
virtualalias02000000/status0/4096bytes, DFclear. All62 protected checks exact,
B diagnostic/owner exact, four frozen manual source pins unchanged. No writes,
launches, C access, driver/Startup changes or new host runtime during collection.

Never relaunch/recollect either409 attempt. Original decoder failure retained;
final-review.json is the historical pending-B record, pair-review002 closes it.
Both observed allocation prefixes succeeded; original407 failure cause and later
relocation/paging/handoff remain unknown. No route-causality/reliable-boot claim.
Next review the exact relocated copies and paging/far-jump boundary, then design
a fresh bounded discriminator if needed; no speculative allocation patch.
Six clean-install FATX long paths and strict event failures remain separate.
Working physical demo and all rollback bytes preserved; no public release/tag.

#409 PHYSICAL001 CLOSED; paired File Explorer diagnostic pending

Read outputs/launch-wrapper409 REPORT/DESIGN/NEXT/final-review and actual
stage/launch/collection. One FTP probe accepted2026-10-16 00:45:44UTC; complete
80-byte report/dashboard by00:46:06; collected00:46:16. All62 sampled protected
files/Startup/hives/events exact. Originallauncher/drivers/settings unchanged;
no Windows boot or dashboardC access. PayloadVA81f00000/PA01f00000, loader
VA82000000/PA02000000, virtualalias02000000/status0/size4096, DFclear. Only the
instrumented allocation prefix succeeded. Historical407 cause/paging/handoff
stillunknown. Firstparser wrongly excluded the inclusive32MiB page start;
originaldecode.py/collection failure retained, interpretation002 separate.

B is staged/readback exact at E:/Applications/XWNBoot409b/default.xbe. NO host
launch. User asked to run ONCE via UnleashX File Explorer and report dashboard
return (diagnosticonly, notWindows). On answer write manual-user-return002.json
then manual.py collect ONCE. Never repeat A/collection/build/test attempts.
Missing report does not prove noentry. Rootdemo251 ticket retained, no active
host processes. Existing working demo remains E:/Applications/XWNEBoot/default.xbe.

Build003 compiled from exact374 wrapper/header/payload, same300624bytefootprint;
13 actualx86 hostcases plus capturedreports/129decodernegatives use modeled
kernel/file effects. B variant004 changes only two data cookies, one directory
character and sectiondigest; instructions/layout identical, separate13cases/
129decodernegatives. No emulatorrun. Physical001 is separate actual evidence.
Preserve build001 paddinglength failure and build002 wrongparentpath failure;
neitherdeployed. Privatecapsules E:/xwn409. All9original407sourcepins unchanged.
TransparentNTFScompression of oneclosedfixture/tenhostEXEs/twoRAMcaptures kept
exact fullhashes/paths; no chainmove/delete/rebase. Build20GiBguard unchanged.

SixFATX true longpaths/strictfreshinstall events remainopen. No crypto/SID/COM+
rename/deletion, new FATXdriver, losslessinstaller or publicrelease. PhysicalWMP
windowedvideo/audio confirmed407; fullscreenframedrops retained. Installation
instructions now use observed File Explorer workaround, not a proven menu fix.

#407 CLOSED /408 READ-ONLY: physical Media Player demo confirmed

Read media-physical407 REPORT,final-review003.json,user-result003.json,
collection003.json; launch-route408/menu-inspection001.json and REPORT.
User confirms video fine windowed/audio audible; fullscreen loses a fewframes,
acceptable to user. NormalWindowsrestart then dashboard; one6006, history
preserved, allprotected/demo bytes exact, noapplicationevents, soleFtdisk49
retained. No fullallocation/stereorouting/framecount/freshphysicalinstall claim.
Clip remains C:\xwndemo407\play.cmd (dashboard E). Use windowed for demo.

BothfailedFTP launches and userfrontmenu blackreturn remain preserved. User
reports noXromwellUI/DVDnoise duringfailure. Exact-file launch from UnleashX
FileExplorer did reachWindows/player. LocalXBE extent/sectiondigest/embedded
image valid. 408 read ONLY existing authorized380 menu config C exception plus
Elauncher: liveconfig exactly380, correct E XWNEBoot target/current720p bytes.
No menu edit or otherCaccess/write. Route-dependent cause remainsunknown;
uncheckedXBEallocationreturns onlystaticlead, noobservedallocationfailure.

No hostprocesses, newlaunch or physicaltest queued. All407 launches/collections
consumed; neverrerun. Manual003 is separate userboot. Nineoriginal407sourcepins
unchanged; newcollect-manual003.py used once. Privateevidence E:/xwn407,
menuXML E:/xwn408 private only. No newdrivers/settings/Startup changes.
Docs media-player-demo/validation updated. SixFATXlongpaths/strictfreshinstall
failures remainopen; no publicrelease/tag. Preserve allpriorfailures/rollbacks.

#407 MANUAL003 PLAYING: physical audio heard; await video/normal return

Read media-physical407 REPORT/NEXT,manual003.json,user-playback003.json and
entry-review003/path-review003. User reports failed retry had noXromwell UI,
heardDVD; front Windows menu also black/reboot. Requested exact File Explorer
E:/Applications/XWNEBoot/default.xbe; user reports Xromwell/Windows appears,
then clip loads and audio audible. No new host launch/write. Actual physical
Windows/player/audio user-observed; explicit video motion and fullcompletion
not yetconfirmed. User asked videoquality and normalWindowsrestart whenfinished.
Do NOT interrupt/play/reboot remotely. On dashboardreturn collect-manual003.py
ONCE. Old collect.py alreadyconsumed afterfailedretry, neverrepeat.

Local exactXBE sectionextent/digest/embeddedimage valid; FTPcommand equals398
successfulcommand. Historicmenu notcurrentproof. Reviewedsource fixed E loader,
noDVDfallback; uncheckedallocationreturns are onlystaticlead, NOcauseproved,
NOpatch. Menu/FTP versusdirectfile difference remainsunresolved. No physical
file changes except originaldemoMPEG/play.cmd. No C access this407 work.
All hostprocesses CLOSED. SixFATXpaths/strictfailures/publicrelease remainopen.

#407 RETRY FAILED: early black screen/dashboard return; no playback

Read outputs/media-physical407/REPORT.md,launch001-user-observation.json,
launch002.json,launch002-user-observation.json,collection.json,boot-state002.json
and boot-inspect002.json. Original launch001 FTP200 only dismissed screensaver
per user. User explicitly authorized retry; SINGLE retry002 at2026-10-16
00:05:31UTC acceptedFTP200, FTP went offline, then user saw black/dashboard.
No further launch. User asked whether Xromwell/Windows was visible; pending.

Collection COMPLETE, never repeat. All protected/demo files exact, zero new
system/application events and zero normalshutdowns. All five E system hives
match accepted399 byte-exact/clean headers; video trace matches prior398.
Exact early failure/cause remains unknown. Private evidence E:/xwn407. Physical
playback NOT reached; emulator406 PASS separate. No writes beyond original two
demo files; retry/diagnostics read-only, dashboardC untouched. No candidate
patch, setting change, allocation-scan boot or third launch queued. Host retry
38700 and collection27133 CLOSED. Hardware ticket demo251 retained.

#407 ACTIVE: physical Media Player demo launched; awaiting user observation

Read outputs/media-physical407/REPORT.md,NEXT.md,before.json,stage002.json,
launch.json and source-pins.json. User confirmed dashboard and ready to watch.
Current immutable399 physical E720p/FATX390/video303/audio004/Frollback and
normal Startup verified. Only new E:/xwndemo407/ces2001.mpg and play.cmd written.
Full19,742,720-byte MPEG readback SHAe39bf2aee01eecf993723988b274518f3f75076c6b62d1f263051daadd069619;
99-byte shortcut exact. Windows path C:\xwndemo407\play.cmd.

SINGLE launch2026-10-15 23:58:12UTC acceptedFTP200 using existing E720p entry.
Do NOT repeat launch. No driver/hive/Startup/menu/dashboardC changes. Normal
startup remains; no automatic playback/restart. User asked to open play.cmd and
report actual moving picture/audible speech/stutters/errors. No physicalPASS yet.
On user-requested normal Windows restart/dashboard return run collect.py once
with supplied current FTP environment. Local before captures E:/xwn407/before.
Collection is read-only immutable/media readback plus event deltas, not full
allocation/clean-install qualification. Never infer playback from prior406.

All host transfer/launch processes closed:15792 failedbulk,56962 resumed,
49200 launch. Failed capitalized-password530 preserved; lowercase authenticated.
Credentials must remain private/environment only. BulkSTOR timed out after786432
bytes; original script/receipt and private partial retained. Exact source-prefix
verified before bounded32768-byte APPE/1024-byte blocks; complete final equality
permits launch. No guessed/repeatedSITE. Hardware rootdemo251 ticket retained,
all peer claims closed. Nine source/input pins; no emulator launch this turn.

Six trueFATX longpaths and strict events remain release blockers. No tag/public
release, no other physical test queued. Preserve current media for user demo.

#406 CLOSED: OEM path correction and real Media Player playback

Read outputs/install-validation406/REPORT.md, DESIGN.md, NEXT.md,
final-review.json, emu001/audit.json and media-evidence001.json. Single owned
emu001 launch 2026-10-15 23:21:56 UTC, normal Windows restart/dashboard,
orderly host exit0, no fallback. All owned processes closed. No physical access.
Runtime E:/xwn406/runs/nt5-validation406-emu001; preserve its complete backing
chain. Never relaunch/recollect this case or earlier closed405 cases.

Both original 179-byte 3½ Floppy shortcuts restored through native CopyFileW;
OEM437 observed, original bytes exact after restart. New public FATX name
preflight checks all6475 original paths:6469 representable, SIX genuinely
oversized paths remain. Native43-byte create returns206. No long-name alias,
truncation, crypto/COM+ deletion or new driver installed. General lossless
installer remains BLOCKED on native namespace compatibility.

Native RegQueryValueEx returns DRM DataPath type1028/80 bytes exactly matching
original and independent cold readers. Typed Python decoder still unsupported;
not evidence of storage corruption, not DRM/DPAPI functional qualification.
Strict FALSE remains: six paths, Ftdisk49 and kbdhid1; historical405 PnP256
warnings retained. Exact installed message resources identify dump-pagefile
configuration, redundant HID reports and window notification timeout. No gates
waived or services/events suppressed. Historical0102/0103 dump patches are NOT
current fresh403/390 baseline and cannot be blindly promoted.

WMP6.4 completed archived CES2001 Gates/The Rock clip,190.8 seconds. Private
aspect-preserving MPEG SHA256e39bf2aee01eecf993723988b274518f3f75076c6b62d1f263051daadd069619
at E:/xwn406/media001/ces2001-nt5.mpg. Two actual frames independently match
source; complete captured audio envelope correlation0.993777, reverse/shuffle
controls0.152112/0.030505. Real emulator video/audio PASS, physical playback
PENDING user's console-availability answer. No copyrighted media in source repo.

Cold6556 files/275dirs/254dirclusters,0errors/orphans,five hives/raw-reader
agreement,15 protected paths and three staged files exact.83 private files
rehashed/206 frozen host inputs exact. New scope is a fresh copy CONTINUATION of
405, not another independent clean installation. Existing405 remains unchanged.

Public tests: Windows32 tests (23 pass/9 Linux-only skips), Linux five new
name tests pass. Original errors/failed preparations/derivative preserved.
Public release/tag not ready. Public instructions: docs/installation.md,
docs/validation.md, docs/media-player-demo.md; tools/fatx_names.py.

Storage: ten closed old emulator binaries ZIP-retained/readback-verified,
1,333,767,377 bytes recovered; restore exact member/path/hash before old reruns.
E exFAT hardlink refusal immediately restored original executable byte-exact.
C seven immutable executable and five CAB duplicates hardlinked/readback-verified;
break links before future in-place writes. Transparent NTFS compression retains
logical bytes/paths, including one CLOSED405 assembly image; no backing moved.
All receipts in406. Git pack replacement blocked by automatic approval review;
Git packs unchanged.20GiB reserve still tight: recheck before build/launch.

Physical E720p/FATX390/video303/audio004, dashboard C, F rollback and immutable
0.1.0/0088 unchanged. Private credential files never print/stage/export.
Pending physical demo must inspect current shared lease/installed hashes first,
upload/readback only private MPEG in new E demo folder, no fresh drivers/hives.
Next independent filesystem work follows406 DESIGN; do not silently drop the
six remaining security/application paths or call the general installer ready.

#405 CLOSED: clean customized-SP4 Xbox assembly functional pass

Read outputs/fresh-assembly405/REPORT.md, NEXT.md, qualification001.json,
installed-final001.json and closure001.json. Fresh404 customized-ISO PC disk
unchanged; no old Xbox Windows/user hive payload. New standard 10 GB image,
explicit 130 SYSTEM/1 SOFTWARE value changes and 14 same-ISO dependencies;
fresh403 ten component artifacts plus settings, all 11 unique/15 paths exact.

emu001 missing-FreeLoader failure preserved, never parented. emu002 core boot
passed, audio absent. emu003 capacity-refused BEFORE launch. emu004 genuine
SetupAPI audio/network success, immediate wave test failed while software-device
setup pending. emu005 post-install audio/TCP pass and display PnP completion.
emu006 normal startup restored; manual Run witness: 720p32, 2048 offscreen pixels,
32768 exact persistence bytes, one wave device/audio result0, 32x4096 exact TCP
bytes EACH direction. Normal Windows restart/dashboard. All five launched cases
CLOSED orderly host exit0/no fallback; four normal Windows restarts. No xemu
process at 18:51:34 UTC closeout. No physical access/test queued.

Final cold: 6549 files read/hashed, 274 dirs/253 directory clusters, zero errors
or orphans, five clean hive headers/raw-reader agreement, protected fresh builds
exact. Final disk C:/xwn405/runs/nt5-fresh405-emu006/hdd.qcow2 SHA256
757fbba9179fb990451d7a586e7f6a1695d38cb988e106d3e1a81eaf4de73922.
Preserve its COMPLETE backing chain. 1091 frozen-input checks/409 private files
rehashed; 14 actual qualification mutations rejected. Never relaunch/recollect.

Strict FALSE: eight FATX-writer path exclusions (crypto/Protect/COM+ and non-ASCII
shortcuts), Ftdisk49 and final kbdhid1, prior seven PlugPlayManager256 warnings,
typed DRM DataPath0x404 decoder failure. DPAPI/DRM/COM+ semantics unqualified.
First-boot wizard/private-credential logon remain manual. Private credential file
C:/xwn405/logon-private001.json: NEVER print, stage or export contents. No settings
utility runtime/performance/physical/public-installer qualification.

Extraction/parser/capacity/sparse failures, provision001 case audit, probe003
chkstk link failure and normal-stage005 empty-directory walker failure retained.
Only verified redundant new extraction copies removed; original404 and images
retained, no backing moves. Normal-stage006 full file-map comparison proves only
owned Startup removal plus new manual probe/saved script. No automatic witness
remains. Unsupported-device/welcome prompts remain; no suppression.

Public tests: Linux 27 pass; Windows 18 pass/9 explicit platform skips. UTF-8
notes update retried after a host default-encoding read failed before mutation.
Next portable provisioning contract, explicit path compatibility and strict-event
investigation; pristine host, physical install/recovery and curated source/license
review remain separate. Retail key still pending. Physical E720p390/video303/
audio004, F rollback, immutable0.1.0 unchanged. No tag or publication.

Source-only review bundle: C:/xwn405/source-review001/xwn-source-review405.zip,
SHA2563018f2f558935e038706aa83c1bda3c8872b0346f98ffbb5377ecf90c85dbed1,
535 entries, all readback-verified and repeat packaging byte-identical. This is
private source review, not public release or complete license/privacy clearance.

#404 CLOSED: supplied ISO identities and clean PC media validation

Read outputs/clean-media404/REPORT.md, NEXT.md, final-review002.json and
upstream/windows-media.json. Both supplied ISO SHA256/SHA1 identities freshly
verified; independent Archive.org full downloads/readbacks match exactly.
Retail e3816f6e...386859008bytes/kernel6717; customized OEM75ae5e49...
594280448bytes/kernel7376. Retail clean installation remains PENDING matching
retail key in private local file; user asked, no online key used. All ISO files
read (6157/6806), DRIVER.CAB/SP4.CAB/kernel decompression pass.

OEM001 fresh blank2GiB PC setup phases1..4 CLOSED, all exit0/no timeout/hostkill.
Final disk-only desktop boot had no ISO/floppy; witness manually launched once
through normal Run after setup removed RunOnce. Two normalshutdown records,
no warning/error/application records, exact7376 kernel, clean fivehive headers.
All keys/types/raw bytes agree in two independent readers. Scoped PC install
PASS; strictFALSE typed DRM DataPath0x404 decoder failure and automatic handoff
failure retained. No freshXbox/physical/fullNTFS qualification. Never relaunch,
recollect or silently convert these failures into full PASS.

Original probe001linkfailure, cold001typedfailure,002inline-byte comparison,
003case-sensitive diagnosticpath failure,004phase4 capacity refusal retained.
005 measured sparse projection keeps20GiB reserve; no backing disks moved.
Two identical downloaded duplicates removed after fresh comparison with retained
supplied originals; receipts preserved. Final disk SHAece991e4dc6b662ece2a39dddba384a3c480173cafd89086135f6bb861b7f796.
113private files rehashed; keys/hives/Windows binaries/answerfloppy stay private.
All owned VM/build/download sessions CLOSED; no physical access or test queued.

Public verify-media command + docs/manifest complete. Linux27 tests pass,
Windows18pass9explicit platform skips;13synthetic+7actualqualification negatives
and10rawbounds checks pass. New535-entry private source review003 bundle
C:/xwn404/source-review003/xwn-source-review404.zip SHA
ba47e56b8e4e08e645f428f539b3f93a8536128c4edd9530c29f34b9f7152939.
No tag/publication. Physical E720p/FATX390/video303/audio004/Frollback/0.1.0 unchanged.
Next: matching retail key; new documented owned-media-to-Xbox registry/E assembly
from this clean baseline, not private399 payload; pristinehost and physical
install/recovery qualification still separate. Prior403 builds/restore remain
complete and distinct; do not repeat them without changed inputs.

#403 CLOSED: provenance, dependencies and prepared E restore

Read outputs/release-readiness403/REPORT.md, NEXT.md and final-review.json.
HAL/network source correspondence PASS outside timestamp/checksum bytes;12
Microsoft input files exact to owned media, kbdclass6875 OEM-specific/kernel7376.
Fresh anonymous public fetch, RosBE bootstrap6587-entry receipt and8profiles+
settings11artifacts PASS. All8 full trees reconstruct from extracted531-entry
private source review bundle. Pristine-host setup remains separate.

Install001 factory-root refusal preserved;0026571files verified then hosthivex
load failed; finish003 only continued unstarted restore. Full E backup,32-byte
launcher damage,exact restore/outside identity,6571files/factoryroots/5hives PASS.
Private C:/xwn403/install-restore002/restored.qcow2 preserved; no physical access.
Single instrumentedemu001 accepted2026-10-15 01:33:41UTC, returned01:40:27UTC;
normalshutdown1/orderlyhostexit0,289dirs6610files269clusters0errors/orphans,
5hives/protected hashes/720p graphics/audio scopePASS. Originalaudit/closureFALSE
mode1 expectation retained; separatecorrected-analysis003 pins actual303build
profileOFF/mode0 and rejects30mutations. StrictFALSE soleFt49 remains. No
relaunch/recollect/parenting. Fresh403compiled binaries NOT used in that boot.

All owned sessions CLOSED including51980/3379/13868/38535/54434/15307/67148/87138;
no xemu process in read-only closeout query. Sources and reports committed in
this turn; no tag/publication. Source bundle C:/xwn403/source-review002/
xwn-source-review403.zip SHA4f85564c7b3580a9d08abf24b560931d0ae03ecab86d650b03e5b58efa09b5f3.
Retain source-package001 failed legacy-doc-link partial directory. Existing
historical untracked files untouched. E720p390/video303/audio004/Frollback and
immutable0.1.0 unchanged. Fresh owned-media/registry provisioning, pristine-host
setup, physical install/recovery and final license/export review remain. Do not
publish privateWindows archives/history. No hardware queued.

# Source layout and newcomer guides implemented (402)

Actual maintained source is now under src/ with six independent pinned profiles,
MIT-scoped original work and preserved upstream licenses. New portable tools/xwn.py
reconstructs exact full trees and builds selected components. Six fresh profile
builds plus the settings utility pass (nine artifacts); ten guard tests and49
local guide links pass.37 frozen399/34 frozen401 inputs unchanged. No physical
access, tag/publication or baseline changes. Build hashes are not asserted equal
to installed binaries. See outputs/public-layout402/REPORT.md and NEXT.md.

Remaining: complete HAL/network/input provenance, public dependency acquisition,
clean-machine build and disposable fresh-install/restore qualification. Current
working E720p demo remains unchanged. All owned build sessions closed.

# Source review package prepared; integrated demo unchanged

The separate source candidate is C:/xwn401/package001/xwn-source-review401.zip.
It contains33 verified entries: six exact component source patches, configuration
tools, build/use/recovery guidance, license texts and a release checklist. All six
source trees replay through the exported portable tool; repeat archive assembly
is identical. No new compiler run or hardware operation occurred.

This remains a private review draft. Manual license and remaining component
provenance review, portable complete builds and disposable installer validation
are still required. The private Git history contains many local references and
must not be made public wholesale. No tag, publication or visibility change.
See outputs/public-source401/REPORT.md and NEXT.md. All owned sessions closed.

# Integrated private demo ready; current bundles are399 revision002

FATX390 is now installed and readback-verified on the Xbox alongside video303,
audio004 and normal720p startup.68 protected/hive/control files verified; only
the storage driver changed. Original0101 and F rollback remain. No new boot was
started during integration, and no timed benchmark/restart is left enabled.

Use Windows in UnleashX with the mouse connected before boot; leave the Razer
keyboard unplugged through Xromwell. Current instructions and downloads are
C:/xwn399/README.md and QUICKSTART.md. Preview002 is495kB; private system002 is327MB.
Both are readback-verified, include rollback and corrected build documentation.
The private system archive contains historical Windows/user data, is not a fresh
backup and has not been full-restore-tested. Do not publish it.

Scoped physical file/audio/GDI/shutdown/integrity passed in398, with the preserved
audit identity correction. StrictFtdisk49 remains failed;1080i text/motion issue and
exact stereo routing remain unresolved. No new public release/tag or visibility
change. Next: ordinary user demo feedback, then sanitized source/license/build
and disposable-installer preparation. All owned processes are closed.

# Storage fix passed the physical demo workload; baseline remains restored

October14: candidate390 now returns each exact filename once and passes all six
CMD file operations on the Xbox. Native and CMD copies match exactly, audio/GDI
checks pass, Windows shuts down normally, and cold allocation/hive/protected-file
checks are clean. This follows the setup-first original397 control, which
reproduced the duplicate-listing and CMD MOVE defect.

398's original audit retained the control's expected driver hash by mistake.
It remains preserved. Separate corrected-analysis002 verifies the candidate
against frozen build identity and preserved bytes with unchanged aggregate gates.
Scoped result PASS; strict result FALSE for the retained Ftdisk49 event.

The Xbox is at UnleashX with normal720p startup/original0101/video303/audio004.
No candidate adoption, new bundle or tag yet;395 is still held on failed394.
Next is a new scoped demo acceptance/bundle plan, keeping original rollback and
explicit known limitations.720p text/full-window dragging are user-confirmed;
1080i remains unresolved. All owned sessions are closed; dashboard C untouched.

#720p demo restored; original-driver control completed, storage fix still held

October14:397 settled known-device setup before filework and completed direct
BMP/text copying with exact cold readback, audio/GDI checks and normal Windows
shutdown. Disk allocation, five hives, policies and protected files passed.
The original0101 duplicate-file listing defect reproduced and CMD MOVE failed.
Full qualification remains FALSE; Ftdisk49 is also retained.

The console is back at UnleashX with normal startup, original0101, video303 and
audio004 restored/verified. All owned processes are closed. Next is a fresh
matched candidate390 test with this setup-first order, not another control retry.
394's incomplete copy remains unexplained;395 bundle/adoption is still held.
No new public release/tag/bundle, no changes to dashboard C or original F rollback.

# Historical status below

# 720p demo restored; storage fix and new bundle held

October14:394's FATX390 test stopped during its second CMD copy and was manually
restarted. The file has an exact prefix and zero tail; the cause is unresolved.
The setup helper had not run yet. Normal startup and original0101 were restored.
Allocation, five hives, protected binaries and original F rollback passed.
No normalshutdown or completedworkload; candidate notaccepted and395bundleheld.

396 moved known-device settling before file work using original0101, but produced
no Windows/startup evidence. The dashboard was already reachable at the first
sample; baseline hives/eventlogs/trace are unchanged. All checks/collection are
closed and normal720p startup is restored. Awaiting the user's boot observation;
no more launch is queued. Preserve both failures without assigning a cause.

User-confirmed clean720p text/full-window dragging and the repaired UnleashX
menu remain the demo baseline. Video303/audio004/FATX0101 are installed.1080i's
output problem remains separate. Allownedprocessesclosed; no newpublicrelease,
tag or bundle. Existing privatearchives and originalrollback remain unchanged.

# Historical status below

# 720p demo works; file-operation fix validated in emulator, hardware retest pending

October14 UTC: user confirmed clean text and full-window dragging at720p; watched
boot384 went normally through Xromwell into Windows. E720p374 launcher/display303,
audio004 and originalFATX0101 remain installed. UnleashX Windows entry380 repaired.
1080i photographed text/dragging defects remain unresolved, not promoted by720p.

Physical385 completed graphics/audio/normalshutdown and clean cold integrity but
CMD MOVE rejected one exact file as multiple files. Physical387 returned early
without startup/Windows evidence; originalstate unchanged and startup restored.
Cause unknown; user observation of that short boot is pending. No newhardwarequeued.

Exact0101 source and ordinary389 emulator reproduced repeated exact-name entries.
FATX390 fixes cached nonroot logical indices. Matched392 returns exactlyoneentry;
393 actualNT5CMD copy/move/reopen plus API bytes, audio/GDI/normalshutdown/cold
integrity pass. Candidate remains emulator-only. Both strictresultsFALSE solely
for retainedFtdisk49. No gate waiver, fullfilesystem/physical/release claim.

New383 bundles remain held pending successful physical file validation. Existing
379 private archives/tags/rollbacks remain immutable. Public source/license and
installer checks still apply; no publicupload. All owned emulator/buildsessions
closed. Next: resolve physical387 observation, then one fresh bounded E-only
candidate test with rollback and complete readback before revising bundle gates.
See cmd-regression393/REPORT.md and NEXT.md, fatx-enumeration390/REPORT.md.

# Historical status below

# Integrated demo ready; physical outline observation pending

October13 demo378 launched once at22:23:18 UTC and stays at the Windows desktop.
Current physical E1080i/display303/audio004/FATX0101 unchanged. One-time outline
preference and reversible controls are in C:\xwndemo372. User feedback and normal
restart/readback are pending; no automatic observer or repeated launch.

New377 emulator scoped PASS: corrected settings persist REG_SZ0; actual720p,
combined graphics/audio, normal shutdown and clean cold allocation/hives/protected
files. StrictFALSE soleFt49. Initial373 parser failure retained. E720p physical
qualification remains pending. E-specific inspect/apply/restore selector ready;
oldF selector must not targetE.

Private379 preview and reconstructed E-system bundles readback-verified; see
REPORT.md/package001.json/system001.json. No new tag/public upload. Docs now cover
demo, display, recovery, builds and public-export gates. Source/license/full-build
and disposable installer qualification remain before public release. Other driver
approaches are isolated threads; no unqualified prototype merged.

# Historical status below

# Stretch optimization tested: no benefit, baseline unchanged

October13 matched emulator371 runs passed scoped graphics/audio/shutdown/integrity checks but uploaded identical minimum pixel bytes across960 actual stretch callbacks per build. Do not deploy369 as an improvement. StrictFtdisk49 remains, no event waiver. Both runs and all owned processes are closed; original physical303/normalEstartup/Frollback remain, Xbox C untouched. See stretch-runtime371/REPORT.md and NEXT.md.

The prior physical measurements still place most remaining cost in display uploads. Same-primary fast copying and this clipping candidate produced no material benefit. Meaningful further gains require a separately validated mapping/ownership or GPU architecture change; neither is hardware-ready. Existing bundles/tags are unchanged. No additional hardware test is queued.

# Historical status below
# Physical1080 copy measurement complete; baseline restored

October13 physical368 completed normally. Four real900KiB copies measured median6.372ms into ordinary RAM and10.864444ms into the display buffer, a median paired ratio1.709. Exact pixels/guards and sampled WB/UC mappings passed. This identifies a substantial display-copy cost; it is not a speedup or proof that cache policy alone explains it. See bandwidth-physical368/REPORT.md and NEXT.md.

Normal E startup and original303 display driver are restored; original F rollback retained. Both complete E allocation scans, five hives and protected/device checks pass. All processes closed; no test queued; no dashboard C access. Strict qualification still fails Ftdisk49 and Srv2013, neither waived. Existing private bundles/tags remain unchanged. Next is a reviewed shared-mapping/display-write optimization design, followed by matched emulator qualification before another hardware candidate.

# Historical status below
# Private E bundle assembled; performance attribution prepared

The E payload now reconstructs byte-for-byte twice and has a verified private bundle plus usage/rollback guide in stock-installer343. The new installer correctly refuses the current occupied E target; it is migration tooling for the owned console, not generic provisioning. Its corrected capacity probe and full new install flow still need disposable-fixture runtime validation. The first incompatible fixed-path bundle remains rejected evidence.

Large-area phase probe344 compiles cleanly and passes2008 synthetic parser negatives. It measures driver engine/copy-body/wrapper counters for the existing15large operations; no matched profiling driver run or speed improvement yet. Next qualify a fresh OFF/ON pair in the emulator before hardware timing. Xbox remains unchanged at UnleashX, normal E startup/F rollback/C restriction preserved. All sessions closed, no test queued, immutable releases unchanged. Physical342 event failures still stand.

# Physical E boot complete; normal startup restored

New E installation booted at1920x1080 and passed five drawing samples, six audio API phases, normal shutdown, persisted drive binding and integrity checks. After-scan:616dirs7565files633clusters, zero errors/orphans. E has2,073,346,048 free bytes. Original F rollback and all E/F protected/hive checks pass; Xbox C untouched by tools. No active process or queued hardware test remains.

Overall combined/strict results remainFALSE: the existing Srv2013 warning still refers to dashboard C (Windows F), plus Ftdisk49. No gate or event was suppressed. Read stock-boot342/USAGE.md for E launcher versus unchanged root-menu F rollback. Next: repeatable E-target packaging and continued1080 software drawing work; no release retag or speedup claim.

# E installation verified; physical Windows test active

340 completed all6566 files with readback, zero overwritten files and unchanged F rollback hashes/hives.341 before allocation scan passed610dirs7548files627clusters with zero errors/orphans. One3421080i/audio/drawing Windows boot accepted06:38UTC; observer56264 active. Test Startup is temporary: restore normal E startup first on return, then collect and run the distinct after-scan/audit. No Xbox C access or deletion. See CONTINUATION and actual records; never relaunch this test.

# E installation continuation active; Windows test not launched

Original340 upload closed after4859 verified files with an FTP PASV502 refusal. Its last intended file and launcher were absent on fresh inspection. One owned resume002/session35831 rereads existing files before creating the remainder; no overwrite/delete or Xbox C access. F rollback unchanged. Normal E startup remains.

Next: complete journal/readback gate,341 physical002 before allocation scan,342 physical002 one1080i/audio/drawing/shutdown test, restore normal E startup FIRST on return, distinct341 after-scan and342 cold audit. Original failure retained; no duplicate launch. d19b22f6 pushed; continuation work not yet committed. See CONTINUATION for exact process/artifact paths.

#340 physical E upload ACTIVE;339 repeat boot closed PASS;341/342 prepared only

340 session94070 ACTIVE, E:/xwn340/stage001/journal.jsonl and outputs/stock-stage340/physical001.json are authoritative. Started05:35:01UTC,2400sec bound. Create-only E Windows3roots plusApplications/XWNEBoot, allfiles individuallyreadback, default.xbe LAST. Never rerun stage.py or boot beforecomplete. ExistingF Windows/loader andC untouched. At05:52UTC2518files/~200MB verified; no errors. Sourcepackage337 complete6566files704025709bytes/sevenchanges/fourMountedDevicesaliases,normalstartup. Readonlycapture6566files704005869bytes,all26baseline/fivehivesverified. Efree2.94GB measured333;projectedallocated768884736B, no cleanup.

339CLOSED scopedcombined/repeatPASS,strictFALSEFt49:5drawingsamples/6audio phases,normalshutdown1/dashboard05:31:40/orderlyexit0,clean340dirs6804files357clusters/fivehives/protected,persistedEbinding/alloldtestfiles.338activationdecoderFAILmissingcoverage:zeroactualactivationcalls; no fixclaim/physicalpromotion.336failedwizardtimeout retained,cleanallocation/no normalshutdown. All339processes closed.

341 new read-only nativeE16KiB scanner compiled66e58932...,reportsMUSTonF uniqueApp directory. Host002actualCwalker produces594400byteEXACT independent335coldrecords,ASan/UBSan;host001GCCstylefailurepreserved. NOphysicalscanlaunched. After340complete run341physical.py before launch/observe/collect ONCE then341analyze.py --capture E:/xwn341/physical-before --output outputs/stock-scan341/before/allocation.json. NO Windowsboot unlessallocationclean.

342 physicalEbootcheck prepared locally E:/xwn342/payload, originalphysical201helper (NOT338),samefive-sample smallreplay as339/audio251. Nativefiles/driver installedby340remainHD; testchangesonlynewE/xwnstock342 andtemporaryEstartup. After340+341beforePASS run342physical.py launch ONCE thenobserve. Onreturn collectFIRST restoresnormalEstartup, captures Eevents/hives/logs/INF/protected andverifiesFrollback. Then341physical.py after launch/observe/collect ONCE andanalyze to342physical001/allocation.json; run342audit.py physical001 viaWSLLDlib. AllgatesincludingSrv/Ft49retained;F rollbackexists, noCaccess. No342hardwarelaunchqueuedyet. Frozenhost/payloadpins ready.

Current336-342 workUNCOMMITTED;333-335pushedc7070d5e. AutomationPAUSED;rootdemo251ticketactive,peerclaimsclosed. Seeactualrecords beforeresume,neverduplicate.

# User partition constraint: Xbox C: untouched; E: stock-drive target, F: expanded storage

Read outputs/partition-policy332/README.md and dashboard001.json. User explicitly says leave dashboard C: alone; no writes/deletes/moves there (native Windows F:, the331 Srv2013 warning target). E:/Games deletion is authorized ONLY if E needs space, preserve Apps/Applications. Read-only inventory found E:/Applications and no E:/Games; F:/Games exists and was NOT deleted. No console changes/C access/free-space claim. Target future stock10GB compatibility on dashboardE; expandedF usable. Current Windows maps dashboardE->WindowsD and dashboardF->WindowsC; stock-layout relocation/boot/registry behavior remains unvalidated. C warning retained without suppression/gate waiver. Current baseline and releases unchanged.

#331 CLOSED: drawing/audio/integrity PASS, combined event gate FAIL; baseline restored

Single physical1080i launch accepted03:51:48.621670UTC October13; dashboard04:00:01. All5samples x15large cases, independent pixels/guards, legacydrawing/audio/setup/bindings, normalshutdown1 passed. Srv2013 WindowsF: occurred INSIDE combined interval; scopedFALSE and strictFALSE, plus inheritedFt49. No application events/popup. Read outputs/hd-large-physical331/{REPORT,NEXT}.md and final-review.json/failure-review.json/physical001/audit.json. Pass-gated summarize.py NOT executed; no qualified measurement-summary. Diagnostic960x540 medians: fill31.875ms, RAMupload/WM_PAINT41.667ms, overlap40.263ms. Oneboot/fivesamples; notFPS/speedup/causalbottleneck.

Freshbefore/after SYSTEM map WindowsF: to2359820288, matching historical dashboardC: smallsystempartition. Exact historicalowned message resource decodes diskcapacity warning. Currentfreebytes/systempartitionallocation NOT queried; no inferred FATXcause or deletion/thresholdchange. This is distinct from hostC/E cleanup. NEXT read-only currentcapacity/shadow-C review, then specific body/copy timing discriminator; prior209scalarstores gave no benefit, keepOFF. No speculativeoptimization/GPUgrant or immediate retest.

Collection restored startupFIRST andallsixoriginalbaselinefiles; freshpostscanFTPreadback exact. ONE read-onlyscan completed6227dirs122692files6232clusters0errors/orphans. Fivehives/protected/policy/binding/historygatesPASS; unchangedvideo trace is historical shared-allocation evidence. Physicalaudio004/software118/shared158/FATX0101 restored, dashboardavailable. Allowned331sessions CLOSED: observer97226,collection43115,scanobserver99137,audit47900. Neverrelaunch/recollect331Windows/scan or parent330closedruntime. Frozen1303inputs exact. No hardware queued; rootdemo251ticket retained; automationPAUSED.

Recovery329 COMPLETE on E:/Codex-archive/xbox-windows-native/0.2.0-recovered329; START-HERE.md gives guardedinstall/restore. HDoverlay+sourceZIP BYTE-IDENTICAL originals; combinedrecovery entries exact/newouterhash; Gitbundle complete/tagsunchanged. NoDdrive needed.330 emulator CLOSED scopedPASS/strictFt49 with all75largecases, normalshutdown/dashboard/orderlyexit0, fullcold327dirs6763files328clusters0errors/orphans,5hives58protected. Allrecords/failures preserved. RootREADME updated to privateexperimental0.2.0/currentEguide; historicalsection retained.

#331 physical large-area measurement ACTIVE;330 emulator CLOSED scopedPASS

330 completed all5samples x15large cases/independentpixels, retainedlegacy/audio/setup, normalshutdown1/dashboard and orderlyhostexit0. Cold327dirs6763files328clusters0errors/orphans,5hives58protected. StrictFALSE soleFt49 outsidecombinedinterval. Runner83443/observer2513/audit90946 CLOSED; neverrelaunch/recollect/parent330 runtime. Evidence outputs/hd-large-runtime330/emu001/final-review.json. Recovered329release remains E:/Codex-archive/xbox-windows-native/0.2.0-recovered329; originaltags unchanged;8fbd1be6 pushed.

331 physical ONE accepted SITE at03:51:48.621670UTC per actualtrial; observer session97226/PID29964 ACTIVE. Userpersistentkeyboard-unplugged/hardwareauthorization honored. Rootdemo251ticket passed, nopeerowneractive. Read outputs/hd-large-physical331/{package,capture001,preflight001,rollback-tests001,frozen}.json and physical001/{trial,return}.json beforeacting. Fresh1212file rollback/hive/INF capture/fivehivepreflight,10actualrollback-modelcases,1303frozenpins. Same recovered0.2.0 six-file1080i chain,ONLYnew327replay; originalphysical201helper retained. Probe folder /F/xwnhd331; startup TEMPORARILY enabled. No driver optimization/registry change.

NEVER launch331Windows again. On dashboardreturn run physical.py collect ONCE with supplied credentials viaXWN_FTP_HOST/USER/PASSWORD; it restores startupFIRST, preservescandidatebytes and restoresallsixbaselinefiles. Then scan001.py physical001 launch ONCE, observe, collect; unique /E/Applications/XWNHD331scan. Analyze allocation with native-windows-fatx-preflight/analyze.py on331artifacts/physical001/allocation tophysical001/allocation.json, run331audit.py physical001 inWSL/offlinedisklibrarypath, closeout.py freshFTPreadback, summarize.py. KeepstrictFt49; no claimsbeforefullcold gates. Observer1200sec doesnotforceconsole; if stillofflineafterbound askoncescreen. Noautomaticretry acceptedoruncertainSITE. Preservealloldrecords. AutomationPAUSED;currentturn owns followthrough.

#330 large-area emulator run ACTIVE;329 recovery COMPLETE on E:

Exact322 emulator and311/316/303 binaries recovered from retained WSL build outputs, all original full hashes.0.2.0 overlay and source ZIPs reassembled BYTE-IDENTICAL; combined private demo all entries exact with new outer ZIP hash; complete Git history verified, tags unchanged. Package E:/Codex-archive/xbox-windows-native/0.2.0-recovered329, current START-HERE.md. No D: needed. Read outputs/artifact-recovery329/REPORT,USAGE,final-review. No physical access.

313 helper recompiled pinned source/compiler; initial mismatch only COFF timestamp/checksum, bounded reconstruction found EXACT original full hash. Preserve helper001 mismatch and helper-metadata001 success. New329 never-executed seed from retained251 has distinct container hash9cfc49c2...; all6795 files/339entries compared, ONLY seven exact replacements, namespace/entrymetadata unchanged,322dirs6752files323clusters zeroerrors/orphans,5hives. Original317 disk not claimed identical. First read-only verifier followed valid emptydirectorycluster0 and refused; original retained,002 corrected/pass.

330 prepared new child replacing ONLY327 replay. Single launch accepted03:39:29UTC per host receipt; actual user-facing date follows client context. Runner83443/PID22052 and observer2513 ACTIVE; inspect records, NEVER duplicate. Newports5104/5105/5106, E:/xwn330, full build/xemu leases, recovered322 executable.1200secondhost/1260observer, unchanged180sec guest per replay.238source+11host pins exact beforelaunch. Physicalbaseline unchanged; automationPAUSED.

After owned normalreturn or bound, collect once via330audit under WSL/offlinedisk library path; require all five327large verdicts PLUS unchanged setup/audio/fullcold/event/normalrestart gates. Run review-combined then final-review; preserve failure if incomplete, no hardwaremeasurement until actualcorrectness. All330frozen inputs immutable. metadata-clarification.json records inherited329 historical-pin/beforeartifacts descriptions as parent-only; actual current maps and local hives are authoritative. Don't edit frozenfixture or waivegates.

#326 guarded HD deployment/restoration PASSED; baseline restored

New tools/deploy-hd.py + hd_overlay.py provide prepare/apply/restore for immutable0.2.0 overlays with26-file prerequisites, frozen inputs, exclusive ticket/tool lock, local exact rollback copies and per-write/readback journal. No boot API. Host00142 modeled-transfer cases and sharing001 two actual Windows handle cases PASS. Physical001 prepare00:47:03->00:47:13UTC, apply00:47:49->00:47:57, restore00:48:02->00:48:11 October13:6HD writes/6restores, all26files exact after, startup/HAL unchanged. NO Windows launch, allocation scan, registry edits or full-system restore. Baseline audio004/software118/shared158/FATX0101 restored. All sessions CLOSED, exclusive lock released; demo251 ticket retained, automation PAUSED. Never rerun consumed326 IDs. Unknown/partial bytes refuse automatic restore and are preserved privately; power-loss recovery remains unqualified.

Read outputs/hd-deployment326/REPORT.md,USAGE.md,NEXT.md,final-review.json and physical001 receipts; privatepreimagesD:/xwn326/physical001. All42host cases used exactreleasebytes/actualcore but modeledFTP. Windows transient/permanent journal sharing tested independently. v0.2.0tag and bothbinary/sourcearchives unchanged.

Read-only performance-review rehashed ten closed315/324 logs. Same256x128probe binary: medianRAMupload370/374ops/s; window40-roundoracle420ms both. Stats snapshots195/435ms lie outside timing. These are within-boot microbenchmarks, NOT FPS or independentreplications. NEXT specificdiscriminator: new bounded large-window probe on unchanged0.2.0driver with separate timing/oracle and actual copied-byte/clip counters, emulator correctness first then new physicalcontrol. No speculativecache/GPUchange or hardwarelaunch queued. KnownFt49 andallpriorfailures preserved.

# 0.2.0 private release push confirmed

Private remote main d8086050 and annotated v0.2.0 were verified after atomic push; tag resolves to25b41b7e. Source/history and both binary packages are complete, hashes/readback verified. Repository check30972files passed;14releasefiles exact inindex. See release-0.2.0/push-receipt.json and USAGE.md. All build/test sessions closed; no physical access or deployment; baseline restored, automation paused. Packaging/tagging work is complete. Future work is a plan, not an active test.

# 0.2.0 private experimental HD release tagged and archived

v0.2.0 is immutable at25b41b7ea47850cab21c649d9661ffd18497348e (tag object7dccac7060ed682cf4647ed955599c422528dd6f). User confirmed normal-looking1080 output; observation is separately recorded without editing324/325 frozen verdicts. Private overlay and combined recovery/demo archives are complete and readback-verified. Tagged source archive30965blobs exact; complete-history Git bundle verified for0.2.0/0.1.0. See outputs/release-0.2.0/README.md,USAGE.md,bundle.json,source-evidence-bundles.json,REPORT.md andcloseout.json. Artifacts atD:/Codex-archive/xbox-windows-native/0.2.0. Archive helpers001/002 failed before archive creation;003 completed, all originals preserved, tag never moved. Push is a separate final closeout step.

No physical access/new experiment/new capture this turn. Console last verified restored audio004/software118/shared158/FATX0101, no hardware test queued, automationPAUSED. Scoped release accepted; strictFALSEFt49, WAVE_MAPPER diagnostic limitation, exactstereo/repeatboots/otherencoders/GPU/fullrestore limitations retained. Immutable0.1.0/0088 and historical256recovery unchanged. Next plan: repeatable install/recovery and repeated HD validation, measured video performance, device integration, sanitized public source/build recipes and supportedxemu upstream changes. Do not rerun consumed trials or package IDs.

# 0.2.0 private HD release assembled; tagging next

The user reported: "The video output had looked normal at 1080". This new observation is separately recorded in outputs/release-0.2.0/user-observation.json; original324 machine verdicts/pending observation and staging325 remain unchanged. Physical315720p and3241080i scoped workloads/integrity passed; strictFALSE Ftdisk49 retained. No new hardware access, deployment or experiment. Baseline audio004/software118/shared158/FATX0101 remains restored. Automation PAUSED; no owned processes/test queued.

Private final overlay and combined demo/recovery bundle are complete and every entry readback-verified at D:/Codex-archive/xbox-windows-native/0.2.0. Overlay1242000bytes SHA474957aa6d2eb4cd8c3818a26ad0568e4b9c104b8159891c065b1491c8f6930d; combined334214426bytes SHA8136a98edda6cd239fb41ffd7ce59f44ab53e0f794cabacc212dca9de8026065. Existing256 recovery ZIPs/manifest rehashed unchanged, included as historical recovery, not a new snapshot or restore-tested whole disk. Read release-0.2.0/README.md and USAGE.md. Packaging is not a full compiler rebuild, public publication or permanent install. Stereo/repeated boots/other encoders/GPU acceleration remain unqualified. Preserve0.1.0/0088/all failures.

Next closeout: repository and exact stage checks, commit/tag v0.2.0 once, private push, source/evidence archive and Git bundle pinned to actual tag; then record receipt without moving tag. Later project work: repeatable deployment/recovery and repeated HD validation, measured video performance, device integration, sanitized source/build recipes and xemu upstream review. No new experiment launched by this plan.

# Physical1080i workload passed; visual confirmation pending

Five1920x1080 drawing samples, six audio test phases, normal restart and cold allocation/hive/protected checks passed in324. Full F scan found zero errors/orphans. Original startup and all six baseline files are restored/readback. No test is queued. The TV/Windows picture report is still pending; Ftdisk49 remains a strict failure.0.2.0 is untagged.

A private staging bundle with720p/1080i overlays, baseline recovery and usage instructions is readback-verified under D:/Codex-archive/xbox-windows-native/hd-staging325. It is an upgrade for the current demo, not a full installer or release. Read ../hd-physical324/REPORT.md and ../release-staging325/USAGE.md. Existing256 recovery and immutable0.1.0 remain unchanged.

# Physical 720p workload passed on watched retry315

Five drawing tests at1280x720x32, six audio phases, normal restart and cold allocation/hive/protected checks passed. The user saw a correct-looking picture. Original baseline restored and read back; no hardware test is queued. Strict qualification remains false solely for Ftdisk49. Earlier314 boot failure remains unexplained; Windows1080i and0.2.0 remain pending. Read ../hd-observed315/REPORT.md.

# Hardware720p returned early; working baseline restored

313 completed the720p emulator drawing/audio/restart/cold checks.314 hardware returned after21seconds with no test logs and unchanged Windows event/hive/trace bytes. Its boot-stage cause is unresolved; screen observation requested. All original boot/video files and startup were restored/readback. Full allocation, hive and protected checks are clean. No further hardware run queued. Next expose actual loader stage/result before reset;1080i and0.2.0 remain pending. Read ../hd-physical314/REPORT.md and NEXT.md.

# 720p Windows workload passed in emulator

Actual1280x720x32/pitch5120, five drawing phases, six captured audio phases, normal restart and clean allocation/hive/protected checks passed in313. Ftdisk49 remains a strict failure. The new foreground activation code was never called because the three wizards were already in front; its missing coverage remains a failure, not a proven fix for312. Physical baseline unchanged;720p hardware and1080i Windows testing remain,0.2.0untagged. All owned313 processes closed. Read ../hd-ui313/REPORT.md and NEXT.md.

# 720p desktop reached; unattended setup gate needs handling

The new explicit720p Cromwell path compiles and reaches a1280x720 Windows desktop
in the emulator. Actual emulated mode registers agree. Its test did not qualify:
the known-wizard helper waited for foreground/active status, timed out with zero
actions, and correctly blocked measurement. A late capture shows Welcome in front.
The exact failing earlierGUI predicate was not logged. No normal shutdown; owned
host closure was orderly and allocation/hive/protected checks are clean.

Matched control passed drawing/audio/normalrestart/coldintegrity; knownFtdisk49
remains strictFALSE. Next address explicit, identity-checked foreground handling
in the test helper while retaining device/setup gates, then revalidate unchanged
720p driver in a fresh fixture. Hardware and1080i remain unqualified;0.2.0untagged.
Physical baseline and recovery are unchanged. Read ../hd-loader311/REPORT.md and
../hd-boot312/REPORT.md. All owned sessions closed at this checkpoint.

# Mapping and software HD bounds validated; timing integration remains

The9MiB framebuffer is outside Windows-managed memory and mapped uncached across
all19 observed process roots. The software driver now has a reviewed opt-in bounds
check covering1920x1080 when returned memory lengths permit it.

Its matched ordinary720x480 emulator pair passed drawing, audio, normal restart
and cold integrity checks. KnownFtdisk49 remains a strict failure. No physical
driver changed, and Windows1080i is not yet qualified.

Next: complete the Conexant timing/readback reference, implement720p/1080i in the
native handoff, then test on the connected TV.0.2.0 remains untagged. Read
../hd-mapping302/REPORT.md, ../hd-surface303/REPORT.md,
../hd-regression304/REPORT.md and ../hd-timing-reference305/DESIGN.md.
C is below20GiB buildguard; recover verifiedclosed artifacts before next build.

# Nine-MiB reservation passed its Windows workload; HD timings remain next

The coordinated loader/bootvid/miniport candidate now boots Windows through the
HDTV path with a9MiB framebuffer reservation. Both matched emulator runs passed
five drawing samples, six audio phases, normal restart and full cold integrity
checks at720x480. The driver recorded successful acquisition at the new55MiB base.
The existing Ftdisk49 remains a strict failure; no physical driver changed.

Next verify the live reserved pages/shared mapping, lift the software display
image-size guard, then integrate720p/1080i timings. The physical standalone HD
patterns already worked, but Windows1080i and release0.2.0 remain unqualified.
Read ../hd-reservation301/REPORT.md and ../hd-reservation300/NEXT.md.

# Full Windows relocation check passed its scope; repeated HD pattern completed

The relocated bootloader completed the existing Windows audio/drawing workload
and normal restart in a matched emulator pair. Both cold integrity audits passed;
the known Ftdisk49 remains a strict failure. This pair used the composite profile,
not the physical HDTV cable path, and retained the4MiB framebuffer.

The user reported the physical HD pattern looked good. The requested repeat also
completed its720p/1080/fallback buffer checks and returned to UnleashX. Windows
and its installed drivers remain unchanged. Next: HDTV-path relocation boot,
coordinated9MiB framebuffer reservation, then actual Windows HD timing support.
0.2.0 remains untagged. Read ../launcher-windows296/REPORT.md and NEXT.md.

# Launcher relocation passed its isolated startup check

The prerequisite for a larger framebuffer now compiles and reaches both emulator
startup checkpoints with its code and stack relocated safely below40MiB. The
original physical launcher is unchanged. Windows handoff and1080i timing integration
remain next; standalone physicalHD buffer checks passed, TV report still pending.
0.2.0 remains untagged. Read ../launcher-runtime295/REPORT.md.

# Physical HD mode path verified; Windows integration remains

The new connection exposes HDTV modes. A single standalone test selected720p,
1920x1080 and fallback, verified13.2MB of framebuffer CRCs, and returned to
UnleashX. TV visual confirmation is pending. The Windows/audio baseline is unchanged.
Next is relocating the bootloader away from HD framebuffer memory, then a shared
boot/display reservation and timing implementation.0.2.0 remains deferred.
Read ../hd-physical292/REPORT.md and NEXT.md for scope and preserved failures.

# Standalone HD mode milestone completed, Windows integration pending

290 verified720p,1920x1080 API mode and return to640x480 in the emulator, with
13,209,600 exact independent framebuffer bytes and orderly cleanup. This is not
physical1080i or Windows HD qualification. The known one-byte reserved-sector
strict disk failure remains recorded. The new work does not alter the physical
Windows/audio installation. Read ../hd-output290/REPORT.md and NEXT.md.

Next: a coordinated Windows boot framebuffer layout and encoder/timing handoff.
The existing reservation is too small; enlarging it overlaps launcher code/stack.
Physical tests will need a component/HDTV-capable adapter and1080i display.
0.2.0 stays deferred until stable. No new automation or release tag.

# October12: 1080i preparation, release deferred

The authorized video inventory288 confirmed Conexant and64MiB. The current HDMI
adapter presents standard AV; only640x480 and720x480 are exposed. Saved HD flags
do not override the cable detection. Physical1080i testing needs a component/HDTV
capable adapter/cable and1080i-capable display. Current Windows/audio drivers,
startup and five hives are unchanged. The console returned to UnleashX.

Next is emulator-only HD mode/timing validation and a coordinated Windows boot
framebuffer layout. 0.2.0 is not tagged; prior overnight automation stays paused.
Read ../video-capabilities288/REPORT.md and NEXT.md. GPU retirement is deferred.

## Preserved combined demo status

# October11 combined demo preview

Current installed physical: FATX0101, exact tested display118/shared158, genuine
ACI207 audio004. No speculative PCI/USB prototype. Original0088 and immutable
0.1.0 remain preserved. Root owns the demo251 hardware ticket.

Combined253 six audio API phases plus five GDI workloads completed and returned
normally. Its original binding-equality failure is preserved; separate narrow
raw-hive review proves six inactive ACI values matched preexisting active values.
Repeat255 passed original equality unchanged, full allocation, five hives and
protected hashes. Strict FALSE remains the inherited Ftdisk49 error. User heard
login sound and confirmed the louder trio in256; the quiet trio was unheard.
Exact speaker routing is not confirmed.256 returned normally; its physical-output
ID query instead returned the mapper, retaining the diagnostic failure. Full
allocation, five hives, protected hashes, exact bindings and normal
restart passed in256; the original mapper-ID and Ftdisk49 failures remain. See
[256 observations and cold results](../demo-audio-level256/REPORT.md).

Private254 overlay reproduced identical SHA8000eb0e12de3688fb3b922f9f7763eb9198295ffef4579421f447da689b6b39,
15 entries497820bytes, all entries readback verified. This is packaging repeatability,
not a full source rebuild or complete system recovery. New private file-level recovery capture completed:6638files879661149bytes
in330directories, both system/boot-dashboard ZIPs allentries verified. It is not
a disk image or restore-tested release. See demo-audio-level256/capture-summary.json. Repository remains private. Existing Windows root menu verified.

Remaining demo gaps: exact left/right speaker routing, known unsupported APU/PCI/USB
wizards, crash-dump configuration warning; preserve these limits. Software text
upload reductions are already bounded-physical-tested; no GPU
acceleration,1080i or additional mode is claimed. Full reconstruction/public-release
licensing and xemu upstream work remain separate unfinished goals.

The latest actual emulator milestone is the [matched282 unit-reference release
and guest reuse](../release-pair282/REPORT.md). Four selected texture units were
released while their cache owners remained, then the real guest rebound the same
objects with exact source/RGBA/framebuffer checks. CPU/context and full known
owner graphs were captured before, after release and after guest work. Both
attempts closed orderly. This proves that narrow transition, not complete backend
retirement or a native Windows GPU handoff. The standalone fixture's strict disk
comparison still fails one reserved-sector byte; filesystem bytes stayed inherited
unchanged, but the writer is unattributed and the gate is not waived. This is
separate from the Windows Ftdisk49 warning and the physical demo.

The next step is actual cache-owner disposal and replacement. [283 through287](../disposal-boundary287/NEXT.md)
provide host-tested disposal, generation accounting, publication, completed-free
hooks and an explicit four-boundary contract. No new xemu binary, guest run or
physical deployment has installed those pieces. The actual graph provider,
four-boundary worker and independent runtime transport still need integration.
Known failed negative tests and all predecessor results remain preserved.

A read-only check of the audio, PCI and USB chats near03:50UTC October12 found
all three inactive/completed, with no new hardware test dispatched. Their selected
demo recommendations remain: audio004, current keyboard/mouse support, no USB
XID prototype or speculative PCI package. The louder tones are user-confirmed;
the output mapper query does not identify a physical output device. No peer
was asked to start more work during this closeout.

# Earlier status preserved chronologically

# Actual loader handoff traced — October10,2026

One fresh debugger child pins five executing Cromwell/FreeLdr boundaries and
verifies532480 raw memory bytes. GPU registers,20KiB RAMIN and84KiB reserved
CPU tail remain unchanged across USB removal, interrupt revocation and transfer.
22 valid channel0 object-table entries survive, including the proposed blit
classes. PFIFO1/PGRAPH0 invalid context and disabled hardware switching persist.
CPU cleanup, normal restart and independent cold integrity checks pass; strict
whole-boot FALSE remains the sole inherited Ftdisk49 error. No source/binary
driver change, GPU writes/grant, acceleration or physical access occurred.

See [225 report](../video-loader-handoff225/REPORT.md) and its raw/evidence review.
All owned sessions are closed. Next is an explicit ownership transition accounting
for old-owner ranges, bounded backend retirement and software context service.
No further quiet-register repetition is needed; current state cannot grant
firmware object reuse. Physical0101/video0093,0088rollback and0.1.0 preserved.
Two CLOSED historical standalone probes were hash-verified/offloaded with original
paths retained as junctions, restoring C: above the unchanged20GiB guard.

## Earlier status

# Native GPU preflight completed — October 10, 2026

Matched ordinary emulator runs now exercise a bounded read-only FIFO preflight
under real NT5 FileObject, generation and kernel-mutex ownership of a CPU lease.
The control performs zero GPU reads; the candidate completes 128 reads. Both
pass 65 allocations/releases, four joined workers, normal shutdown/dashboard,
full cold allocation, five structural hives and 28 protected hashes. The same
Ftdisk 49 error remains a strict failure; no gate was waived.

All eight candidate snapshots agree: PFIFO channel 1, PGRAPH channel 0, current
context invalid, push/pull disabled, zero DMA pointers and IRQs. Quiet registers
do not establish producer/backend retirement; the model does not maintain the
needed busy/status fields. Every reply therefore refuses GPU ownership. See
[224 report](../video-fifo-retirement224/REPORT.md) and its independent pair and
state reviews. All owned processes are closed. Genuine handoff, context service
and bounded completion/drain remain prerequisites to acceleration.

This pair uses the captured physical-core policy and exact targeted wizard
Cancel helper, without synthetic null bindings. No physical deployment or device
branch integration occurred. FATX0101/video0093, 0088 rollback and immutable
0.1.0 remain preserved; this checkpoint does not claim a display speedup.

## Earlier status

# Emulator setup settled for graphics work — October9,2026

Two ordinary boots now complete setup and guarded normal restart in a disposable
emulator configuration. An original exact-ID package explicitly labels the audio
processor, SMBus controller and synthetic PCI test function unused, with no
function service or binary. The subsequent boot retains identical bindings and
adds no SetupAPI records. This is configuration completion, not audio/SMBus support
or a Windows race fix; the physical console remains unchanged.

Both boots pass five graphics samples,20copy checks,25timing loops,50scanout RGB
checks, normal shutdown/dashboard, full allocation, five hives and protected files.
The exact inherited Ftdisk49 remains a strict failure; no new popup/application
errors or gate waiver. Failed host backing-path attempt is preserved separately.
See [sequence report](../device-settled-reboot181/REPORT.md) and its independent
sequence-review.json. All owned sessions are closed. Next target measured DIB
upload/engine costs, then additional video modes. Physical0101/video0093,0088 and
immutable0.1.0 remain unchanged.

## Earlier status
# Paired physical timing166 completed — October8,2026

Fresh baseline/candidate boots each passed five probe samples,20pixelchecks and
25timingloops, with normal restart and exact post-collection baseline restoration.
Median readback25.44x and overlapping copies10.59–10.92x faster. Fill throughput
0.697x and upload0.601x baseline. Raw variance retained; no window-drag FPS claim.
Only the inherited Ft49 error, no new application events/popups; strict release
stillFALSE. Physical0101/video0093 remains installed. Next: existing driver
identity/hook/byte/coherence counters before changing rendering/upload code.

## Earlier diagnostic

# Physical drawing diagnostic164 completed — October8,2026

The optimized stack passed four live copy checks and five bounded GDI loops on
the console, with a normal restart and correct persisted bindings/shared trace.
Original display/SYSTEM restored and readback verified. Sole Ftdisk49 retained
as strict failure; no new application errors or popups. Historical timing suggests
large readback/overlap gains but slower fills/uploads; fresh paired measurements
are next. No permanent candidate installation or new video-mode qualification.

## Prior status (superseded above)

# October8 physical-stack display compatibility and hardware diagnostic preparation

The optimized shared-UC/RAM0112 display stack passed ordinary drawing and normal
restart on a reconstruction containing actual physical159 core/SYSTEM/SOFTWARE,
with only3displayfiles/2typedbindingtokens changed. Same1024x576x32/60 runtime,
successful shared acquisition, retainedbindings, exactprotectedbytes/5hives/full
allocation, no applicationevent/popups. StrictFALSE for samephysicalbaseline
Ftdisk49; never treat this as release or physical qualification. Fresh unique
one-shot helper165 also passed its real child/restart/cold checks. Hardware packet164
is prepared with local/console rollback and restore of0093 display/SYSTEM after
collection. Await actual unpluggedRazer/UnleashX state; no deployment/launch yet.
Physical0101/video0093 unchanged;0088/0.1.0 and all failures preserved. Earlier saved
640defaults were not active-mode proof. See164/REPORT.md and continuation for exact
artifacts, failures, sourcepins and next command. No running owned process.

# Native Xbox Windows 2000 status — 8 October 2026

2026-10-08: the reviewed xemu CPU-write surface eviction now has a qualified
isolated ordinary Windows timing comparison,with identical guest RAM0112/probe141.
Affected192x96 bottom draw median4.387ms to0.098ms (44.678x),while equal-area top
rectangles and memory-only paths stay near their former costs. Both runs pass
strict pixel/event/cold-integrity gates. This is an emulator microbenchmark gain,
not physical FPS or a guest-driver latency comparison. See
[Windows timing report](../video-windows-timing156/REPORT.md).

The guest display improvement is already written and functionally validated:
RAM0112 cuts actual window-movement copy bytes4.71% and repaint bytes17.50% with
exact pixels. Physical latency gain remains unmeasured. An offline three-file
shared-UC provider/miniport/display candidate and qualified0093/historical rollback
are bundled/readback-verified; deployment_ready remains FALSE pending fresh physical
state/binding/rollback review and a display-only emulator reconstruction. The older
0.1.0 miniport mismatch was caught/preserved,then the correct0093 artifact used.
No physical files/settings were changed. See
[candidate bundle158](../video-hardware-candidate158/README.md).

Additional video modes including1080i and WC/GPU-transfer acceleration remain
implementation work with separate geometry/encoder/ownership/physical validation.
The128GiB dump/recovery emulator closure remains complete. Physical0101/video0093,
0088rollback,immutable0.1.0 and unresolved physical SetupAPI corruption remain
explicitly distinct from the newer emulator stack.

2026-10-07 15:45 UTC: the128GiB crash-dump defect is corrected and validated end
to end in the emulator. CandidateATAPI0105 selects the genuine extended ATA
routine; complete64KiB writes at148440145920 match runtime payloads, the lower
wrapped alias is unchanged, and a separate boot saved an identical readable
Windows minidump. Both matched ordinary storage/TCP runs passed strict gates;
controlled crash/recovery passed their distinct gates. Original crash image
preserved. No physical deployment. See [closure report](../atapi-dump-lba48/REPORT.md).

The clean emulator stack additionally contains HAL0102 dump-usage tracking,
FATX0103 resident pagefile extent mapping and NVNet0104 resident shutdown helper.
Inherited emulator device policy and restored matching HidServ remain explicit;
none of these results promotes physical0101/video0093 or changes0.1.0.
Original111-byte physical SetupAPI damage remains unresolved. Next work is
[scoped in the handoff](../atapi-dump-lba48/NEXT.md).

2026-10-07 04:37 UTC: matched aligned first-install control/GDI diagnostics both
passed. Drawing began before the target log entry and completed4688 cycles;
all220 target bytes at270225 survived cold readback. Normal shutdown, events,
five hives and allocation passed. Hardware anomaly remains unresolved; no driver
or physical change. See [installer/drawing report](../fatx-install-draw/REPORT.md).

2026-10-07 04:08 UTC: paired paced append control and GDI-load emulator runs passed:
16,384 total appends,32 exact cold files, normal shutdowns, event/hive/allocation
checks. Drawing completed1,644 cycles and overlapped every append case. No
corruption reproduced or physical change; no video-speed claim. See
[drawing/write report](../fatx-draw-append/REPORT.md).

2026-10-07 03:54 UTC: two fresh aligned first-install diagnostics passed. The actual
post-copy warning landed at the physical log offset270225 in both, including
sector offset401, and all220 bytes survived cold readback. Normal restarts,
event deltas, five hives and full allocation checks passed. Physical anomaly
remains unresolved; no hardware or driver change. See
[aligned installer report](../fatx-install-alignment/REPORT.md).

7 October 03:23 UTC: two repeated-append runs passed 16,384 appends and 32 exact
cold files. A separate UI-assisted first GPU installation on0101 also passed its
cold checks, adding5300 ASCII-only SetupAPI bytes and restarting normally. No
corruption reproduced; actual installer log offsets differ from the physical
anomaly. Physical state is unchanged and that anomaly remains unresolved. See
[sequence report](../fatx-append-sequence/REPORT.md) and
[first-install report](../fatx-first-install-0101/REPORT.md).

7October02:53UTC: two fresh emulator append-boundary runs passed96 cases each,
including the exact physical log offset. All192 files matched cold expected
bytes; normal restart, hive parsing and allocation passed. No new unexpected
events; SetupAPI unchanged. This serial explicit-flush test did not reproduce
the first-install log anomaly. Physical state is unchanged. See
[append report](../fatx-append-boundary/REPORT.md) and its next-stage plan.

7October01:46UTC update: authorized X/Y cache cleanup reclaimed1.39GiB after
verified private backup. A read-only raw-C scan found the508.6MB shadowc.img and
exactly matched Windows'2,932,736-byte free-space reading; no corruption/orphans
or C deletions. The supported GPU INF and a single DevicePath change are staged,
with SOFTWARE rollback preserved. After confirmed keyboard readiness, the single
controlled setup boot was accepted at01:52:08UTC. First collection confirms GPU registration and unchanged binaries, with a new
malformed SetupAPI span still unresolved. User-authorized second boot was accepted
at02:09:25UTC and has now been collected after normal shutdown. GPU registration
persisted; all3439 binary hashes, nine hives and full F allocation pass. No new
log anomaly or popup; one raw-C Srv warning and other device prompts remain.
User-assisted configuration is verified; strict/unattended qualification is not.

Early7October emulator follow-up: the ordinary fifteen-minute0098 workload
passed after supported GPU setup and an emulator-only null-device INF. New
concurrency tests then proved two separate FATX deadlocks: regular-file cleanup
versus volume flush, and rename's parent-directory cache flush versus volume
flush. Candidate0101 separates ordinary-file and directory-stream lock ordering.
Two independent five-worker500-round runs and the full fifteen-minute mapping/
BMP persistence soak passed all workload, normal-restart, event, exact-file,
five-hive and allocation gates. Candidate0101 is eligible for a controlled
hardware trial, not physically or release qualified. One controlled physical0101/video0093 concurrency trial launched at00:50:29UTC
on7October, with0098 rollback and startup preserved. Its13-minute observer expired without dashboard return. User photos then showed
the desktop and all five500-round workers complete in62.205seconds with zero
API errors; restart was deliberately held for pending device installation. Cold
checks now confirm exact test files, normal user-assisted shutdown, full allocation,
3439 binaries and nine structural hives. Strict qualification still fails on the
held automatic protocol and threeSrv warnings. No owned process remains active. See
[continuation](CONTINUATION.md) for evidence and the hardware handoff.

The project has reached a usable native desktop milestone. It is still an
experimental system with incomplete device setup and bounded, rather than
general, stability qualification. Windows runs on the Xbox CPU and stores its
ordinary files on FATX; xemu is the separate development/test environment.

## Established physical capabilities

- Boot screen and desktop; keyboard, mouse and drive browsing.
- User-observed Notepad, Calculator, Solitaire, Command Prompt and Paint use.
  Later Paint saves/reopens were independently checked. The earlier isolated
  save freeze has no demonstrated root cause and must remain in the history.
- User-reported ping, Pinball and the OpenGL Pipes application. These are not
  bulk-network qualification or evidence of hardware-accelerated OpenGL.
- A root-level Windows entry in UnleashX. Video0093 subsequently passed two
  physical boots without resetting its diagnostic trace between them.
- Current installed state: FATX0101/video0093 with normal startup restored.
  Original0098 driver/startup saved locally and in /F/xwn101a. The bounded physical
  workload and cold integrity checks completed; strict qualification remains FAIL.
  Original0088 rollback and the immutable v0.1.0 release remain preserved.

## Storage and stability

The v0.1.0 snapshot preserves the earlier qualified0088 milestone. Post-release
FATX0098 fixes leakage of allocation slack beyond EOF in paging reads, including
the demonstrated odd-length driver-image checksum failure. The focused physical
trial passed. The completed third fifteen-minute0098 soak passed527 checks,
16 synthetic BMP API cases,50 exact final files,34 absent intermediate files,
full allocation consistency,3,439 binary hashes and nine structural hives.

That soak's strict overall result remains **FAIL**: one shutdown-time rundll32
popup and three Srv2013 low-space warnings were recorded. The warnings map to
small Xbox system/cache partitions, not the large Windows boot volume. They are
retained as failures under the existing gate; no silent waiver or new
PASS-gated recovery capture has occurred.

Emulator tracing reproduced the popup and located its hard-error call in
win32k during late device installation. Other traces observe a PnP token
close/use race and late creation failing with invalid handle. Clean controls
do not establish a popup fix, and the failing emulator device identity cannot
be assigned to the physical console without physical evidence.

The latest [GPU package experiment](../shutdown-device-install/README.md)
completed a normal installation using unchanged physical-baseline binaries.
Its first run still recorded the popup and missed dashboard return. Three independent
replays of the installed state retained registration and
passed bounded workload/shutdown checks without a popup. Full F: allocation
checks on the input and two latest replays were clean, with reserved marks
unchanged. These are independent replays, not consecutive reboots or proof of a
fix. The first-install failure still prevents promoting a hardware package.

A subsequent [paired idle test](../shutdown-install-idle/README.md) removed the
explicit mapping/BMP workload. Both runs waited two minutes and restarted
normally. The unchanged control had no popup; the package installed correctly
but still emitted the shutdown popup. Both allocation audits were clean. This
narrows the reproduction to a first-install/shutdown scenario without requiring
the explicit storage workload; the ordinary pair alone does not identify the
failing process or establish a universal cause.

A subsequent [minimal trace](../shutdown-idle-trace/README.md) of the exact
package seed reproduced the same popup. Its owner is rundll32 running newdev
for emulator PCI1B36:0005. Matched win32k raises the hard error before winlogon
enters kernel shutdown. Cold installation, selected binary/hive checks and
full F: allocation pass, but the popup remains a strict failure. Creation,
resume and termination ordering were not captured; debugger timing and this
emulator device identity cannot be generalized to the physical console.

[Source research and a host event recorder](../native-event-recorder/README.md)
now identify that emulator device as the QEMU PCI test device used by xemu as a
memory-controller placeholder. The new recorder captures selected lifecycle
events without debugger stops. One disabled/enabled pair passed bounded cold
checks, and the enabled run captured 423 verified records. It observed a failed
late installer creation and termination during shutdown, without the popup.
The subsequent fixed reproduction batch captured the failing lifecycle too:
creation succeeds, the placeholder installer executes and raises the GUI
shutdown error, then terminates with0xc0000142 before PnP receives shutdown
control5. A separate unchanged run follows the clean invalid-handle path.
See [the captured sequence](../native-event-recorder/FAILING-LIFECYCLE.md).
The recorder still has no demonstrated zero-overhead guarantee, and no
synchronization fix is qualified.

The [window observer](../shutdown-installer-windows/README.md) answered the next
question: the GPU wizard waited at its successful Finish page. Completing it
exposes a restart question, then the next unsupported device. The
[completion experiments](../shutdown-installer-completion/README.md) confirm
that cancelling the next wizard only clears that boot; it returns on a later
boot. A pending-install guard correctly withholds restart in that state.
One earlier observer run also stalled during kernel volume flush; it remains
unresolved and is not explained away by the installer findings.

An [explicit emulator-only null package](../shutdown-null-placeholder/README.md)
now configures the unused QEMU test function without a function driver or
changed hardware identity. Normal setup and an ordinary subsequent boot pass:
the queue becomes idle, no installer recurs on the subsequent boot, normal
shutdown returns to dashboard, and cold event/hash/hive/allocation checks pass.
Both the original short workload and a full fifteen-minute workload passed527
checks and cold audits, including normal shutdown and dashboard return. The
emulator parent still contains the earlier01B0/01B4 FAILEDINSTALL flags; those
are absent on hardware. This configuration avoids outstanding setup; it does not repair the original Windows
shutdown synchronization race or establish physical device support.

A fresh [read-only physical snapshot](../physical-pnp-followup/README.md) verifies
the installed baseline is unchanged. Its latest SetupAPI records still name
the unsupported Xbox01B0 audio function, and GPU PnP registration is incomplete.
Historical emulator/PC entries also remain in the hive; registry presence alone
does not mean those devices are present on the console. No hardware package has
been deployed from these emulator experiments.

## Graphics and device support

The current physical display path retains the inherited framebuffer mode.
Window dragging is visibly slow. There is no qualified rendering acceleration,
Windows mode switching,720p or1080i implementation. Mapping and display-driver
prototypes have useful emulator results but are not promoted to hardware.
Device installation, repeat boot and display lifetime handling must pass before
performance changes are judged in a matched hardware test.

Audio, bulk TCP transfers, long mixed-application sessions and electrical
power-off still need development or qualification. Running a program is not
equivalent to qualifying every subsystem it can use.

## Release, documentation and reconstruction

- v0.1.0 is tagged and has private, readback-verified system/boot/source recovery
  bundles. A full restoration of those archives has not been tested.
- FATX/platform findings and Linux-oriented notes are written in this directory.
  They include post-release EOF findings. No external project has been contacted.
- Reusable Xbox development skills are installed and versioned in the project.
- Fresh reconstruction builds seven native components plus the Cromwell launcher.
  Repeated assembly produces identical overlay packages, and a rebuilt overlay
  passed an emulator boot/GDI workload. Complete bootable-system reconstruction,
  toolchain portability and deterministic compiler outputs remain open.
- The repository is private. Public-export/provenance/data review is underway;
  Windows binaries, firmware and personal recovery material are not public assets.
- xemu changes are inventoried. Networking changes and synthetic diagnostic
  resource changes are distinguished; no upstream issue or PR has been submitted.

## Next gates

Complete and validate real device installation in disposable emulator fixtures,
including a subsequent boot, then retest the shutdown workload without error
suppression. Preserve controls and distinguish emulator-specific devices from
physical support. After an eligible candidate exists, run a bounded hardware
trial and restore/reverify the baseline as appropriate. Graphics speed/modes,
network/audio qualification and a sanitized reproducible public release remain
separate work streams.

Latest experiment details and actual running-process state are maintained in
[CONTINUATION.md](CONTINUATION.md). The evidence index is [README.md](README.md).
