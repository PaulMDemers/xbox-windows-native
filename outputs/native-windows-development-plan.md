# Native Windows development plan for Paul's Xbox

**Latest checkpoint, 3 October:** Windows 2000 reaches its desktop in a private 64 MiB Xbox emulator through UnleashX, Xromwell and the native loader/HAL. IDE storage, the framebuffer miniport and USB input have worked; the Ethernet miniport passes DHCP, ping, repeated disable/enable and memory/disk/GUI endurance checks. A PCI interrupt-trigger correction improves USB boot reliability, and stereo audio passes thirty playback cycles in the combined endurance run. Repeated boot testing also fixed reads of fragmented NTFS files with multiple attribute extents. See the [current implementation report](native-windows-nt5-kernel/README.md) and [physical test prerequisites](native-windows-nt5-kernel/HARDWARE-PREFLIGHT.md).

The physical Xbox has not been tested. The stages below describe the development plan and its original completion gates; the current implementation report takes precedence for progress.

Start with **Windows 2000 Professional SP4 x86 on the existing 64 MiB Xbox**, using UnleashX to launch a separate experimental bootstrap. The console is softmodded and has previously booted Linux through Xromwell. That establishes a useful launch path; it does not yet establish a Windows-compatible handoff. The target is Windows running directly on the Xbox CPU and hardware.

## Media to supply

**Media received and inspected:** both Windows 2000 ISOs are now present. The actual installed fixture uses the supplied OEM **Windows 2000 (SP4).iso**, including its updates and unattended configuration. **EN_WIN2000_PRO_SP4.ISO** supplies original SP4 driver files for compatibility work. The earlier proposal to install the retail image was superseded by the available matching OEM installation path. The [inspection report](windows-2000-media-inspection.md) and [hash manifest](windows-2000-media-manifest.json) record the evidence. No additional ISO is needed for the initial stages. The checklist below remains the specification for later targets.

Local file paths are sufficient. Keep original images unchanged; the development process will hash them and work from copies. Product keys should be entered locally when installation requires them, rather than included in chat or logs.

| Priority | Media | Details |
| --- | --- | --- |
| First Windows test | **Windows 2000 Professional, x86, full installation ISO, preferably SP4 integrated** | Prefer English for consistent diagnostics. Use a clean original image or a faithful rip of your own disc, with the matching installation entitlement. An SP4 update CD alone does not contain the full OS. |
| Alternative to the above | **Full Windows 2000 Professional installation ISO plus the matching-language SP4 full/network installer** | We can prepare and hash a reproducible SP4 source. Avoid the old web/express installer, which depends on external downloads. |
| Later, after the 2000 platform works | **Windows XP Professional, 32-bit x86, full installation ISO, preferably SP3** | Inventory another edition/service pack if that is what you already own before acquiring anything else. XP x64 is not a target for this CPU. |
| Separate later branch | **Windows 98 Second Edition full installation ISO** | A startup floppy image may also be useful if the disc is not bootable, but is not needed for the Windows 2000 work. |
| Optional development material | **Period Windows DDK, debugging tools and matching symbols, if already available** | We will identify the precise compiler/DDK requirements during the source audit. Do not acquire an arbitrary SDK ISO now. |

Microsoft's SP4 documentation distinguishes the standalone update from an integrated Windows installation and documents integrating SP4 with installation files. [Microsoft-authored SP4 readme, archived](https://www.zx.net.nz/mirror/www.microsoft.com/windows2000/downloads/servicepacks/sp4/ReadMeSP-2.html).

**Only the Windows 2000 media is needed initially.** The source audit and a self-authored loader diagnostic can start before it arrives. No Linux ISO, proprietary Xbox XDK, Xbox game ISO or prebuilt ReactOS ISO is required for this plan. Existing Xbox development tools and firmware assets will be inventoried rather than replaced.

Do not start by modifying or slimming the Windows installation. A fixed, identifiable baseline makes loader and HAL failures much easier to diagnose. Additional updates and footprint reduction come after a repeatable baseline boot.

## Intended boot chain

```text
Xbox softmod → UnleashX → separate experimental XBE/bootstrap
    → Xbox-aware FreeLoader
    → Windows kernel + compatible HAL + boot-start drivers
    → Windows system volume → minimal desktop
```

Xromwell is the starting reference for the bootstrap. Phase 1 must establish whether to adapt its existing payload handoff or package the loader behind another XBE entry. Its ability to boot Linux does not imply it can directly load Windows or an arbitrary FreeLoader binary. Keep the known-working launch entry available throughout development; no ROM flashing is needed for the initial experiment.

Windows will need some platform support before reaching the desktop. The loader provides the initial machine state and loads files, while the HAL and boot-start drivers must handle the hardware after the handoff.

## Development stages and completion gates

### 0. Freeze the target and choose the source base

Record console revision/video encoder, confirmed 64 MiB RAM, softmod and Xromwell versions, launch paths, video connection and available test storage. The revision and spare-disk availability remain unknown. Inventory the existing development environment without changing shared SDKs or the Linux project.

Compare three source lines before choosing a merge base:

- The [Xbox ReactOS branch](https://github.com/binarymaster/reactos/tree/7c35fc4ead884e1bd0640a9613f652c40bca8b2e) for Xbox boot and platform adaptation.
- The [NTATV ReactOS branch](https://github.com/DistroHopper39B/reactos/tree/afc0127e8f937ab68503d715d948844973756aa1) for explicit Windows 2000/XP loading and retail Windows framebuffer support.
- [Roswell](https://github.com/mborgerson/roswell/tree/1569e2e89fb47cc72b9c704a8884f98200432bd4) for Xbox hardware initialization. Its loader targets its own kernel and is not a drop-in retail Windows loader.

Audit loader parameter structures, NT version selection, memory descriptors, kernel/HAL imports, processor state, PCI accesses and diagnostic output. ReactOS components must be checked against the selected retail Windows binaries; sharing an NT-style interface does not prove binary compatibility.

**Deliverables:** pinned source manifest, build recipe, dependency/ABI checklist and a chosen loader architecture. **Gate:** identify a credible Windows 2000 handoff contract and a way to observe failures after control leaves the loader.

### 1. Prove the bootstrap and memory handoff

Build a separate launchable diagnostic that reports RAM and framebuffer reservations, loads a small self-authored payload, prepares processor state and transfers control. Add visible phase markers and memory-overlap checks. Reserve all live bootstrap allocations, including their full allocation sizes, until they are safe to reclaim.

Use a conservative fixed display mode. Log actual usable memory after framebuffer, loader and platform reservations; do not advertise the entire 64 MiB as available to Windows. Avoid a large RAM-backed system disk on this target.

An isolated xemu instance can help inspect transitions when emulator resources are available. Each result must identify whether it came from xemu or the physical Xbox. Hardware testing follows review of the affected register accesses, especially PCI enumeration.

**Deliverables:** diagnostic XBE/payload, boot trace, memory map and repeatable launch instructions. **Gate:** three cold boots with a verified payload entry and no overlapping live memory allocations. This proves the bootstrap, not Windows compatibility.

### 2. Reach the real Windows kernel and HAL

Hash the supplied Windows 2000 source and record exact kernel, HAL and boot-driver versions. Prepare a minimal, reproducible Windows boot fixture with the appropriate registry hive and driver registrations. Extracted kernel files alone are not an installed Windows system.

Decide how to create that fixture using a supported installation environment available to Paul or an eventual adapted Setup path. If preparing it on another PC, select its intended HAL model from the outset; moving an ordinary ACPI installation and swapping HAL files is not an adequate preparation method. [Microsoft's Windows 2000 HAL troubleshooting guidance, archived](https://ftp.zx.net.nz/pub/archive/ftp.microsoft.com/MISC/KB/en-us/237/556.HTM).

Construct the version-correct loader block, load the kernel/HAL and required modules, and capture execution after the jump. Use emulator tracing or a verified early execution hook to distinguish a Windows failure from a loader failure. A message printed immediately before the jump is not proof of Windows entry.

Investigate HAL compatibility early. The source audit must determine whether a constrained stock HAL can advance diagnostics or a compatible adapted HAL is necessary from the first kernel test. Timers, interrupts and unsafe PCI probes cannot simply be deferred to desktop driver work.

**Deliverables:** hashed boot fixture, loader trace and first kernel/HAL failure analysis. **Gate:** demonstrated execution inside the supplied Windows kernel/HAL, with reproducible fault location or progress marker. This gate does not require a desktop or writable system volume.

### 3. Establish early platform support and boot storage

Work through timer/interrupt initialization, safe PCI access, memory accounting, boot display and the boot-volume path. Test each dependency against the same Windows build before expanding device coverage.

The important storage boundary is that **FreeLoader reading Windows files from FATX does not make FATX or an image file accessible to Windows after handoff**. A Windows filesystem driver also needs a working underlying block device and controller path.

Choose the writable-storage design before attempting full Windows startup:

| Candidate | Benefit | Work or constraint |
| --- | --- | --- |
| Dedicated test disk/region exposing a Windows-readable volume | Can reduce custom filesystem work | Must coexist with the softmod's launch requirements and resolve disk layout, ATA unlock and addressing. A conventional PC disk cannot simply be assumed to retain a working Xbox boot path. |
| Preallocated system-volume image on FATX | Can preserve the existing Xbox disk layout | Requires a boot-start block-device implementation and reliable access to the backing extents; the loader alone cannot provide this. Fragmentation, writes and recovery must be designed explicitly. |

Prefer a disposable test disk or full disposable clone for write experiments, if available. Select the actual layout only after inspecting the launch requirements and disk geometry. Never give unadapted Windows Setup the current Xbox disk as an installation target.

Begin with read-only sector verification against host-generated hashes, then controlled writes to disposable storage, reboot persistence and offline filesystem checks. Integrate the required boot-start services into the fixture's registry. Diagnose boot-volume failures separately from loader failures.

**Deliverables:** platform adaptation, documented storage layout, boot driver/registration recipe and disk test results. **Gate:** Windows can mount its system volume and reach user-mode initialization repeatedly without filesystem corruption.

### 4. Reach a usable Windows 2000 desktop on 64 MiB

Bring up a basic framebuffer display and USB keyboard/mouse through the Xbox's USB hardware. Adapt and register existing compatible implementations where possible before writing replacements. An Xbox-to-USB adapter and basic keyboard/mouse are useful for this milestone.

Keep resolution modest and measure resident memory, paging and available memory at every milestone. If physical-memory pressure blocks startup, determine which allocations are essential and reclaim loader memory correctly before considering optional services. A 128 MiB upgrade is not assumed by this plan.

**Acceptance:** three cold boots to the desktop, working keyboard and mouse, a text file saved and retained across reboot, stable timekeeping, and a clean offline disk check. Record boot duration and memory use on the real 64 MiB console. A screenshot alone does not complete this stage.

### 5. Add device coverage, then XP

After the desktop gate, prioritize reliable reboot/shutdown, Ethernet and basic PCM audio. Examine the existing [ReactOS Xbox GPU work](https://github.com/reactos/reactos/tree/e38fcf5adc74e39f5632addb6a1b275b1a4b5d29) before choosing a graphics implementation, but keep accelerated graphics outside the first desktop milestone; its retail Windows compatibility still needs validation.

Port the proven platform pieces to one exact XP x86 build, repeating the HAL, driver, storage and memory checks. XP on 64 MiB remains a separate usability experiment. Windows 98 SE gets its own discovery phase for BIOS/DOS/V86 and VxD requirements; it is not another menu entry that automatically follows from the NT loader.

## Effort and working method

Planning ranges for one experienced x86/NT developer are **3–7 days for the source audit, 2–6 weeks for loader/handoff work, 1–3 additional months for early NT/platform/storage support, and 2–6 additional months for a minimal desktop**. They are research estimates, not a promise that retail Windows will boot. Source reuse may shorten them; HAL incompatibility or storage design may lengthen them substantially.

The first implementation work package should cover stages 0–1 and the smallest stage-2 kernel-entry experiment. Reassess after 2–4 weeks without observable handoff progress; improve instrumentation or change the loader design before adding unrelated drivers.

Keep task-local source copies and builds, exact source/media hashes, a hardware inventory, repeatable boot fixtures and a test log. Every test records the code revision, Windows build, RAM size, disk image, platform and last confirmed execution stage. Keep user-supplied Windows binaries outside distributable source packages. The existing Linux project is reference material only.

**Next work:** audit the selected FreeLoader sources against the supplied Windows 2000 kernel/HAL and define the diagnostic bootstrap. Console revision and availability of disposable test storage can be resolved during preflight; they do not block the source audit. Windows 2000 media has been supplied; no additional ISO is required now.

See the [feasibility report](windows-on-original-xbox-feasibility.md) and its [source provenance](windows-on-original-xbox-provenance.json) for the supporting hardware analysis and full research limits.

