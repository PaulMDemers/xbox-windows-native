# Native Windows boot on the original Xbox

Feasibility report and staged experiment plan for Paul, 2 October 2026. The target is a bootloader that transfers control directly to retail Windows, followed by hardware adaptation and drivers. Linux-hosted virtual machines are outside the implementation plan. This round performed research and source inspection only: no builds, emulator runs, installation, shared repository edits or hardware modifications.

**Development follow-up:** Paul confirmed a **64 MiB, softmodded Xbox running UnleashX**, with prior Linux boot through Xromwell. The [development plan and ISO checklist](native-windows-development-plan.md) use this configuration as the baseline. Console revision and disposable test-storage availability remain preflight questions.

**Subsequent engineering evidence:** media is now supplied, private source branches are prepared, and the [pre-build audit](native-windows-prebuild-audit.md) identifies a missing Windows 2000 menu-dispatch entry and definite ReactOS HAL export/forwarder incompatibilities. The [build package](native-windows-prebuild/README.md) supersedes this report's initial source-selection and build-preparation recommendations. No Windows boot has yet been demonstrated.

**Recommendation:** start a native Windows 2000 Professional SP4 boot experiment using **FreeLoader’s Xbox platform support plus a newer, explicitly Windows 2000-aware NT loader**, launched through the existing homebrew/Cromwell entry. Aim first for an observable Windows kernel/HAL handoff. Develop the minimum HAL, boot-video and storage support needed to advance it; add desktop video, input, network and sound in that order as dependencies allow. XP x86 can share much of that research. Windows 98 requires a separate DOS/BIOS/VxD strategy.

This is a credible engineering direction, with an unverified Xbox Windows outcome. ReactOS demonstrates native Xbox adaptation. More directly, **NTATV demonstrates the FreeLoader-plus-drivers approach for retail Windows on a non-PC-BIOS x86 appliance**, the original Apple TV. Its hardware is different, so its success does not establish Xbox feasibility by itself. [ReactOS hardware report](https://reactos.org/project-news/reactos-in-2020/), [NTATV author’s account](https://github.com/DistroHopper39B/NTATV/blob/933dfb4aecdedd796a6741f4b91b47a7cb7307d5/Docs/Write-Up.md).

The key qualification to “bootloader first, drivers later” is that **some hardware adaptation may be required before Windows completes early kernel initialization**. A bootloader can load files and establish the initial machine state. It cannot by itself correct every PCI probe, timer assumption or device access made after Windows takes control. That boundary is the first experiment’s purpose.

## Native feasibility by operating system

Judgments below are hypotheses informed by source inspection, not measured Windows results. With a conventional 4 MiB video reservation, the console has about 60 or 124 MiB left before other reservations. These figures are gross capacity, not a final Windows memory map.

| Target | Stock 64 MiB | Upgraded 128 MiB | Main dependency | Recommended position |
| --- | --- | --- | --- | --- |
| Windows 2000 Professional SP4 | Plausible early boot and small desktop research; tight application/pagefile budget | Stronger practical target for a minimal desktop | NT loader handoff, HAL/PCI/timer adaptation, boot storage and framebuffer | First target; choose one exact media/update baseline |
| Windows XP x86 | Early handoff research is meaningful; less than its published 64 MB minimum remains after video | Plausible minimal desktop capacity; less than the published 128 MB recommendation remains after video | Same classes of changes, with XP-specific HAL/kernel/driver ABI and activation checks | Second target once the common loader/platform work is understood |
| Windows 98 and SE | Memory capacity is plausible; legacy hardware assumptions dominate | More application memory, little reduction in platform work | DOS/real-mode BIOS, protected-mode/V86 behavior, VGA and VxD adaptation | Separate branch; SE first, original 98 tested separately |

Microsoft’s archived KB182751 lists 16 MB minimum and 24 MB recommended for Windows 98 generally; KB309004 corrects older Windows 2000 material to 64 MB; KB314865 lists 64 MB minimum and 128 MB recommended for XP. Falling below a published baseline is not proof that a kernel cannot start. It does limit any usability promise. [Windows 98 KB](https://ftp.zx.net.nz/pub/archive/ftp.microsoft.com/MISC/KB/en-us/182/751.HTM), [Windows 2000 correction](https://ftp.zx.net.nz/pub/archive/ftp.microsoft.com/MISC/KB/en-us/309/004.HTM), [XP KB](https://ftp.zx.net.nz/pub/archive/ftp.microsoft.com/MISC/KB/en-us/314/865.HTM).

A successful native port would use the Xbox CPU directly, without CPU-emulation overhead. A fixed software framebuffer could plausibly support basic desktop applications; acceleration is a separate driver project. There are no measurements here supporting boot times, frame rates, video playback or gaming claims. Existing Linux hardware validation establishes useful hardware knowledge, not Windows compatibility. The NT ancestry of the Xbox kernel does not turn XBE boot firmware into the desktop Windows loader or provide the Windows driver environment. [Contemporary Xbox Linux account](https://www.linuxjournal.com/article/6704).

## Recommended boot chain

Proposed chain:

```text
Existing authorized Xbox homebrew entry
    -> private Xromwell/Cromwell stage or equivalent XBE bootstrap
    -> Xbox-aware FreeLoader
    -> Windows kernel + compatible HAL + boot-start drivers
    -> Windows system-volume mount and session initialization
    -> framebuffer desktop, then additional drivers
```

Cromwell is used here as firmware/bootloader code. No Linux kernel remains running beneath Windows. Reuse its hardware initialization where appropriate, but terminate its services and transfer device ownership deliberately. Keep this initially as a separately launched payload; ROM flashing is unnecessary for the first experiments.

| Approach | What it solves | Additional work | Assessment |
| --- | --- | --- | --- |
| Xbox-aware FreeLoader launching NT directly | Replaces the PC NTLDR/NTDETECT path and constructs the NT boot environment | Correct OS-version structures, hardware description, HAL, boot video and storage | Preferred for 2000/XP |
| PC BIOS payload such as adapted SeaBIOS | Provides legacy firmware calls and a conventional boot path | Xbox board support, video BIOS, resource tables, and later Windows device compatibility | Useful fallback or 98 research; broader initial scope |
| Entirely new XBE-to-NT loader | Full control over initialization and handoff | Reimplement PE loading, imports, registry/driver loading, memory and NT boot structures | Avoid unless FreeLoader has a demonstrated architectural blocker |

The inspected 2020 Xbox fork has a concrete trap: its `LoadAndBootWindows` accepts `Windows`/`Windows2003` and `WindowsNT40`, but has no explicit `Windows2000` branch. Its fallback version detection is also coarse. Do not simply rename `ntoskrnl.exe` or assume the old Xbox configuration is sufficient. A newer inspected FreeLoader revision has explicit `Windows2000` handling and version-dependent loading paths. Preserve the Xbox machine implementation while auditing or transplanting that newer NT-loader work. [2020 Xbox NT loader](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/boot/freeldr/freeldr/ntldr/winldr.c), [newer NT loader](https://github.com/DistroHopper39B/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/boot/freeldr/freeldr/ntldr/winldr.c).

At the NT handoff, audit the kernel/HAL PE imports, SYSTEM hive and boot-driver load order; physical memory descriptors and reservations; configuration tree and ARC boot-volume identity; loader-extension size/version; page tables, kernel stack, PCR, GDT/IDT and processor state. The existing source already implements many of these mechanisms. The task is to make their inputs and version contracts correct for Xbox and the selected Windows build. [FreeLoader i386 startup](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/boot/freeldr/freeldr/ntldr/arch/i386/winldr.c).

## Prior evidence and reusable work

The user's lead about ongoing ReactOS work prompted a branch inventory and located three newer references that should be included in the first source audit. The earlier 2020 Xbox fork is a historical reference, not the automatically preferred implementation base.

| Evidence | Date or exact revision | Relevance and limit |
| --- | --- | --- |
| ReactOS Xbox desktop | Official release article 10 April 2020 shows XQEMU; retrospective 2 January 2021 identifies real Xbox hardware | Native NT-style adaptation is demonstrated; retail Windows is not |
| ReactOS Xbox fork | `b80278ab3ca356b53ae715b62e227141e3a0f955`, 25 December 2020 | Loader, memory map, HAL, partition, PnP and video work are inspectable; includes WIP and setup workarounds |
| Newer ReactOS Xbox branch | `binarymaster/reactos`, `xbox-2025`, `7c35fc4ead884e1bd0640a9613f652c40bca8b2e`, 8 April 2026 | Newer Xbox integration candidate; inspected NT loader still needs comparison with explicitly versioned NTATV paths. No retail Windows boot is established |
| Roswell or nxkrnl | `mborgerson/roswell`, `1569e2e89fb47cc72b9c704a8884f98200432bd4`, 31 August 2026 | ReactOS-derived replacement Xbox kernel; valuable boot, HAL, PCI and encoder references. Its purpose is running Xbox software |
| ReactOS NV2A driver branch | `reactos/reactos`, `0.4.16-xbox-gpu`, `e38fcf5adc74e39f5632addb6a1b275b1a4b5d29`, 10 June 2026; authored by Justin Miller | Commit adds Xbox display, miniport/acceleration and OpenGL components; a driver research lead, not verified Windows driver compatibility or performance |
| NTATV | Author write-up at `933dfb4aecdedd796a6741f4b91b47a7cb7307d5`, 18 April 2026 | Documents native XP boot using FreeLoader and adapted boot/desktop video; source project also supports 2000. Apple TV interrupt and chipset choices must not be copied blindly to Xbox |
| NTATV driver/loader source | `afc0127e8f937ab68503d715d948844973756aa1`, 27 August 2026 | Inspectable Windows-version loader handling, `bootvid` and `genfbvmp` provide candidates for adaptation; Xbox memory reservation and device matching still need work |
| SeaBIOS | `rel-1.16.3`, `a6ed6b701f0a57db0569ab98b0661c12a6ec3ff8`, 13 November 2023 | Legacy x86 BIOS reference; no native Xbox Windows result established |
| Historical VMware and QEMU demonstrations | Steil, 1 July 2003; XP uploader, 7 April 2014 | Hosted Windows evidence only; excluded from native feasibility proof and implementation milestones |

Primary links: [ReactOS release](https://reactos.org/project-news/reactos-0413-released/), [hardware retrospective](https://reactos.org/project-news/reactos-in-2020/), [Xbox fork](https://github.com/binarymaster/reactos/tree/b80278ab3ca356b53ae715b62e227141e3a0f955), [NTATV write-up](https://github.com/DistroHopper39B/NTATV/blob/933dfb4aecdedd796a6741f4b91b47a7cb7307d5/Docs/Write-Up.md), [NTATV project guide](https://distrohopper39b.com/ntatv/), [driver source](https://github.com/DistroHopper39B/reactos/tree/afc0127e8f937ab68503d715d948844973756aa1), [SeaBIOS](https://github.com/coreboot/seabios/tree/a6ed6b701f0a57db0569ab98b0661c12a6ec3ff8), [Steil](https://www.linuxjournal.com/article/6704), [XP uploader](https://www.youtube.com/watch?v=gIBPrL4MEOg).

NTATV is especially useful because the author reports fixing both boot-video and desktop-driver integration and discovering a HAL-selection error on physical hardware. This supports testing those layers separately. It does not imply Xbox should use the Apple TV’s ACPI/APIC configuration. Its published account includes corrections, and the revision above is pinned rather than treating all historical instructions as current.

**How the newer work changes N0:** compare [the newer Xbox branch](https://github.com/binarymaster/reactos/tree/7c35fc4ead884e1bd0640a9613f652c40bca8b2e) with the historical port before selecting a merge base; audit [Roswell's Xbox hardware layer](https://github.com/mborgerson/roswell/tree/1569e2e89fb47cc72b9c704a8884f98200432bd4/hal/halx86/xbox) for reusable initialization; and inspect [the NV2A driver commit](https://github.com/reactos/reactos/commit/e38fcf5adc74e39f5632addb6a1b275b1a4b5d29) before budgeting new display work. Only the GPU commit metadata/file inventory was inspected in this round; its implementation and real-hardware results still require audit. No effort reduction is claimed yet.

Roswell's README describes a self-contained `nxldr` plus compressed Xbox kernel flash image and documents an xemu 128 MiB run configuration. That is not evidence of stock-RAM retail Windows boot. More decisively, its loader source passes no ordinary NT loader block: the custom kernel entry constructs that block and processor descriptors itself. Retail Windows does not contain that Roswell-specific entry routine. Reuse individual hardware mechanisms after review; retain a proper retail-Windows loader contract. [Pinned README](https://github.com/mborgerson/roswell/blob/1569e2e89fb47cc72b9c704a8884f98200432bd4/README.md), [inspected loader](https://github.com/mborgerson/roswell/blob/1569e2e89fb47cc72b9c704a8884f98200432bd4/boot/nxldr/loader.c).

No reproducible native Microsoft Windows 98, 2000 or XP boot on original Xbox was established by this review. Forum proposals are leads, not completed ports. RDP/VNC sessions, skins, Wine and later Xbox models are excluded. A native proof must identify the actual Windows binaries, show their execution on the console and demonstrate that no Linux or virtual-machine host remains resident.

## Native platform work

The following is a dependency analysis. Proposed adaptations are hypotheses until tested against an exact Windows build.

| Area | Required work and first boundary to test |
| --- | --- |
| Firmware and entry | Use the existing authorized homebrew entry and an independently staged XBE/Cromwell payload. Do not begin with ROM flashing. Establish CPU mode, GDT/IDT, paging, caches, DMA shutdown and device ownership at handoff. An Xbox BIOS image, XBE loader, or Linux boot protocol is not an implementation of PC BIOS services |
| PC boot services | The ordinary 98 route needs a DOS boot sector/IO.SYS environment; 2000/XP use NTLDR, NTDETECT and a loader parameter block. Supply disk INT 13h/EDD, video INT 10h, keyboard INT 16h, memory discovery and required BIOS data structures, or replace the loader path with an Xbox-aware implementation. Optical boot additionally needs a suitable El Torito path; XDVDFS/XISO and a PC installation ISO serve different boot contracts |
| Memory | Describe real RAM and every reservation accurately. Protect loader code/heap, stacks, boot parameters, firmware services, framebuffer and DMA regions. Validate 128 MiB initialization and detection rather than assuming an emulator RAM setting is sufficient. Audit MTRRs/cache policy and aliasing |
| PCI and interrupts | Implement safe configuration-space access before the first Windows scan, including scans after boot. Establish BARs and interrupt routing, PIC masks, sharing and trigger modes. Test a uniprocessor PIC configuration first; do not invent an APIC/ACPI topology merely to satisfy detection |
| Timers and reset | Adapt the PIT frequency and check RTC/timekeeping against an external clock. Handle SMC/SMBus power, eject and reboot behavior. A boot with incorrect time or unserviced interrupts is not a usable platform |
| Storage | First prove read-only IDE/ATAPI transfers, then bounded writes and flushes. Start with PIO; add DMA after integrity tests. Arrange ATA unlock before use where required. An ordinary Windows MBR/FAT/NTFS parser does not understand the Xbox partition scheme or FATX |
| Display | Preserve a known boot framebuffer initially. Implement boot/setup output and a separate Windows desktop driver path. An initialized linear framebuffer does not automatically give Windows a VGA BIOS, text mode or supported display miniport |
| Input | Provide boot-time keyboard access, then transition to Windows USB OHCI/HID drivers with correct resource ownership. Use a USB keyboard/mouse via an adapter; the Xbox controller protocol is a separate driver problem |
| Audio and network | Defer until boot, disk and input work. Investigate a small PCM driver and an NDIS driver. Similar nForce branding or matching an INF does not establish register, DMA, interrupt or OS-ABI compatibility |

The historical porting HOWTO identifies dangerous PCI probes, absent legacy keyboard hardware, USB on IRQ 1, a **1,125,000 Hz** PIT instead of **1,193,182 Hz**, and television-encoder setup. Its graphics compatibility wording is broad; it should not be read as certification of PC NVIDIA Windows drivers. These quirks explain why a stock “Standard PC” configuration is only a starting hypothesis. [Xbox Linux porting HOWTO, preserved by XboxDevWiki](https://xboxdevwiki.net/Porting_an_Operating_System_to_the_Xbox_HOWTO).

The ReactOS source makes the adaptation concrete: its Xbox loader supplies machine-specific detection and I/O callbacks, its HAL has a separate clock table and PnP implementation, and its video miniport exposes one already-initialized mode. This is reusable design evidence, not evidence that those binaries can be dropped into Windows 2000 or XP. [Loader](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/boot/freeldr/freeldr/arch/i386/xbox/machxbox.c), [clock](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/hal/halx86/xbox/clock.c), [PnP](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/hal/halx86/xbox/pdo.c), [video miniport](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/win32ss/drivers/miniport/xboxvmp/xboxvmp.c).

### RAM map and storage design

Use this as a **proposed reservation model**, not a complete discovered map:

| Physical range | 64 MiB console | 128 MiB console |
| --- | --- | --- |
| Installed DRAM | `0x00000000–0x03FFFFFF` | `0x00000000–0x07FFFFFF` |
| Example top 4 MiB video reservation | `0x03C00000–0x03FFFFFF` | `0x07C00000–0x07FFFFFF` |
| Gross remainder | 60 MiB | 124 MiB |

Carve loader/firmware allocations and any PC-compatible low-memory holes out of that remainder; never advertise the whole range as free. Read the actual framebuffer address, size and pitch. Windows/DOS firmware compatibility may require IVT/BDA/EBDA and ROM areas below 1 MiB even though the Xbox is not an ordinary PC. Device MMIO and flash are not extra RAM. ReactOS supports a Multiboot map and otherwise synthesizes one while reserving video; its detection code tests 64 versus 128 MiB. Do not run that destructive RAM probe casually from a live host. [Pinned memory code](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c).

Native storage needs a separate design: a disposable PC-partitioned disk, an explicit reserved sector range with a compatible driver, or a boot-start virtual-disk/container driver. Merely loading NTLDR from FATX does not let Windows mount its system volume afterward. ReactOS developers documented the partition-parser problem, and the Xbox fork carries partition and DVD workarounds. [ReactOS developer discussion, 2005](https://lists.reactos.org/hyperkitty/list/ros-general%40reactos.org/thread/KO6WRG3VUAMKEXRDYQPWWYKVVMTWM3QK/), [Xbox HAL initialization](https://github.com/binarymaster/reactos/blob/b80278ab3ca356b53ae715b62e227141e3a0f955/hal/halx86/xbox/halinit_xbox.c), [DVD workaround](https://github.com/binarymaster/reactos/commit/f996aa1032426aaf953a3b562829b64b96f82238).

### Blockers specific to each operating system

**Windows 98 and SE:** native dependencies are a functioning real-mode BIOS/DOS environment, protected-mode and virtual-8086 transitions, safe PCI discovery, working VGA/display behavior, an IOS/VxD storage route, and boot-to-desktop USB handoff. There is no NT HAL to replace. Sharing some WDM interfaces with NT does not remove the VxD and legacy-platform dependencies. Disabling ACPI/PnP BIOS detection can narrow an experiment, but cannot emulate missing hardware. Treat original 98 and SE as separately pinned test images; use SE when its separate native branch begins. [Microsoft setup-switch documentation, archived KB186111](https://www.betaarchive.com/wiki/index.php/Microsoft_KB_Archive/186111), [Walter Oney, Microsoft Press, 1999](https://www.bitsavers.org/pdf/microsoft/windows_2000/Oney_Programming_the_Microsoft_Windows_Driver_Model_1999.pdf).

**Windows 2000 Professional:** native dependencies are a correct NT loader handoff, a compatible HAL with Xbox timer/interrupt/PCI adaptations, safe bus enumeration, boot-start storage, boot video followed by a display miniport, and USB input. The initial research configuration should avoid ACPI and target uniprocessor PIC operation. The recommended starting point is an Xbox-aware FreeLoader with audited Windows 2000 support; this combination has not yet been proven on Xbox. A ReactOS HAL’s internal kernel dependencies must be audited against Windows 2000 SP4; loader success alone does not establish HAL compatibility.

**Windows XP x86:** shares the NT adaptation categories but requires its own kernel/HAL/loader ABI checks, exact service-pack testing and license/activation path. Microsoft documents selecting a Standard PC HAL with F5 or bypassing ACPI checks with F7; this does **not** solve Xbox timer, PCI, storage or display differences. Native 128 MiB is the meaningful research configuration. XP x64 and Embedded are different products and are outside this plan. [Microsoft KB299340, archived](https://ftp.zx.net.nz/pub/archive/ftp.microsoft.com/MISC/KB/en-us/299/340.HTM).

An alternative native NT approach is a PC BIOS payload plus sufficient firmware/device compatibility to keep stock Windows drivers and HAL usable. SeaBIOS is only one part of that approach. BIOS routines cannot intercept every subsequent PCI configuration access or device MMIO operation. A resident virtual machine monitor would change the project into virtualization and is outside the requested native scope.

For all native paths, a fixed framebuffer driver is the first graphics milestone. 3D acceleration, mode switching across Conexant/Focus/Xcalibur encoders, DirectDraw/Direct3D behavior and games are later projects. Xbox AC97 is similar to AMD hardware but uses MMIO; AC97 codec compatibility does not make a PC audio driver sufficient. ReactOS has an open nvnet driver with Xbox-specific interrupt handling and an XQEMU workaround: useful source, but not a verified Windows driver on physical Xbox. [ACI research](https://xboxdevwiki.net/ACI), [ReactOS nvnet at 0.4.15 source revision](https://github.com/reactos/reactos/blob/22fb3bb2c1d8196cf501edbb49b3814739f7b016/drivers/network/dd/nvnet/nvnet.c).


## Driver order and boot volume decision

Treat driver work as a dependency chain rather than waiting for a full desktop before beginning it:

1. **Early platform support:** safe PCI access, timer/interrupt behavior and the kernel/HAL contract. Test a PIC-oriented uniprocessor configuration based on actual Xbox hardware. Evaluate stock HAL behavior only with observable failure capture; plan for an Xbox-compatible HAL or targeted adaptation if it cannot work. ACPI tables are not the first requirement for a non-ACPI NT boot.
2. **Boot visibility:** framebuffer-capable boot output and bugcheck display. Investigate the NTATV/ReactOS `bootvid` implementation separately from the desktop driver. Match imports, calling conventions and metadata to the exact Windows release.
3. **Boot storage:** a usable boot-start controller/volume path and a SYSTEM hive that loads it. The loader’s own successful disk reads do not satisfy this requirement. Capture an `INACCESSIBLE_BOOT_DEVICE` failure as a distinct later milestone, not a loader regression.
4. **Desktop and input:** fixed framebuffer miniport/display integration, correct device registration, OHCI/HID and keyboard/mouse. Test input during handoff; avoid a compulsory interactive setup screen before input exists.
5. **Secondary devices:** network, PCM audio, orderly power/eject handling, then mode switching and GPU acceleration. Full power management and suspend are later features.

The framebuffer candidates are actual source projects, but their initialization/registry path is part of the port. A driver that loads in ReactOS does not automatically load in Windows. [Pinned generic miniport](https://github.com/DistroHopper39B/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/win32ss/drivers/miniport/genfbvmp/genfbvmp.c), [pinned boot video](https://github.com/DistroHopper39B/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/drivers/base/bootvid/framebuf/bootvid.c).

**Storage choice for the first milestone:** load the necessary Windows files read-only from a task-owned payload reachable by the loader, without repartitioning the Xbox disk. Verify whether the chosen FreeLoader revision actually reads the required filesystem; add a narrow reader or preloading mechanism if necessary. This is enough to investigate kernel entry, not to promise a complete Windows boot.

Before progressing to a desktop, choose between a disposable PC-partitioned disk/explicit test partition and a native boot-start container driver over existing Xbox storage. The former reduces Windows volume-driver work but needs a separately reviewed hardware/storage arrangement. The latter preserves the existing layout but adds a substantial early driver dependency. Do not imply that an NTFS file placed on FATX will automatically become a Windows boot volume. Keep FATX access, IDE access and the guest Windows filesystem as three distinct implementation concerns. A RAM-disk desktop would consume the scarce RAM and needs its own NT boot support; it is not the initial plan.

Preparing an installed Windows volume on a conventional PC may simplify first boot; it is merely preparation for native Xbox execution. It does not demonstrate that Windows Setup runs on Xbox. Design native installation and recovery only after the running system’s storage/input path is stable.

## Recommended first experiment

**Experiment N1: observable native NT handoff, targeting Windows 2000 Professional SP4.** Use 128 MiB hardware if already available; retain 64 MiB as an explicit configuration and early-loader target. No RAM upgrade or firmware flashing is part of N1.

1. Record console revision, RAM, encoder, disk/interface, existing boot entry and input devices. Pin the accepted Cromwell base and the selected FreeLoader/NT-loader sources in independent task-owned copies. Reconcile their build tools and licenses without updating shared SDKs.
2. Build a diagnostic payload that enters through the proposed boot chain and records RAM reservations, framebuffer geometry, safe PCI inventory, relevant interrupt state and read-only storage identity. Do not run unrestricted PCI scanning or destructive RAM testing on the existing system.
3. Use a tiny self-authored NT-handoff test payload to verify the loader’s mappings, stack and parameter pointers, with visible stage codes. Its success proves loader mechanics only; it is not a Windows boot.
4. With Paul’s licensed media available, load the exact Windows kernel/HAL, SYSTEM hive and required boot modules. Validate PE imports and version-specific structures offline. Reserve enough memory for diagnostics and preserve immutable source files.
5. Attempt the native handoff with network/audio/acceleration out of scope. Capture the last loader stage, actual kernel entry where observable, first HAL initialization or bugcheck, and the next blocking dependency. Classify a black screen as an unresolved failure unless execution evidence establishes progress.

**N1 success:** repeatable loader entry on three cold boots; identical verified file reads; no reservation overlap; and evidence that Windows itself reached its entry or an early kernel/HAL callback. A breakpoint/trace in xemu may establish the emulator result. On hardware, use an instrumented compatible callback or reliable early display/debug path; a message printed just before jumping to Windows is not sufficient.

**N1 failure and decision:** if the loader itself fails, repair entry, memory or storage before touching Windows drivers. If Windows enters and fails on HAL/PCI/timer behavior, continue with that identified adaptation. If it reaches boot-volume mounting, advance to the native storage milestone. Stop blind boot retries after a reproducible failure without new diagnostics. After 2–4 weeks without a diagnosable Windows execution boundary, review the loader base or the debugging method rather than claiming a broad no-go for native Windows.

## Phases and effort ranges

These are planning ranges for one experienced x86/NT developer with existing Xbox/Linux knowledge. They are not commitments or benchmarks. Toolchain reconstruction, undocumented behavior and hardware availability can dominate. Work stays in this task’s directory or independent source copies; the integration checkout and its source maps remain read-only.

| Phase | Deliverable and go or no go gate | Rough person effort |
| --- | --- | --- |
| N0 Source and ABI audit | Choose FreeLoader base; enumerate Xbox platform changes and Windows 2000/XP version contracts; inventory media/tools and storage choices | 3–7 days |
| N1 Loader and handoff | Diagnostic payload, valid memory/processor transition, captured Windows entry or first kernel/HAL failure | 2–6 weeks; reassess diagnostic approach at 2–4 weeks without observable progress |
| N2 Early native NT | Correct timer/interrupt/PCI behavior, repeatable kernel initialization, boot-volume path and useful crash output | 1–3 additional months; stop expansion until one exact OS build is repeatable |
| N3 Minimal Windows 2000 desktop | Fixed display, USB input, persistent file save, cold reboot and clean shutdown | 2–6 additional months, highly uncertain; a roughly 3–9+ month total native prototype budget is reasonable |
| N4 XP adaptation | Audit XP ABI, exact service pack, boot/desktop video registration, storage and activation; repeat N2/N3 tests | 1–4+ additional months if the 2000 platform layer transfers |
| N5 Native Windows 98 branch | BIOS/DOS/V86 and VxD proof, then disk/input/display integration | 2–6 weeks discovery; 6–12+ months for a possible usable prototype, with substantial failure risk |
| Later device coverage | Ethernet, PCM audio, mode switching, supported hardware revisions and recovery | Scope after desktop evidence; 3D acceleration is a separate major project |

**Go:** native loader research based on FreeLoader, beginning with the smallest observable NT handoff. **Conditional go:** full Windows 2000 desktop once early platform support and a boot-volume architecture are proven. **Follow-on:** XP after explicit compatibility checks. **Separate branch:** 98 because its boot/runtime model differs. A ROM-integrated bootloader, broad hardware support and accelerated gaming are later decisions rather than N1 prerequisites.

For a native desktop acceptance milestone, require three cold boots, keyboard/mouse operation, saved-file persistence, an offline disk integrity check, and stable timekeeping measured against an external clock. Proposed initial usability thresholds are desktop within five minutes, typical input response within one second and small text saves within five seconds. These are acceptance choices to revise after measurement, not predictions. Run stock/upgraded RAM tests separately and record pagefile behavior. A splash screen or one desktop screenshot does not satisfy these gates.

## What xemu can establish

xemu is an Xbox hardware debugging aid for this native port, not the deployment architecture. It can test the boot chain, memory mappings, loader structures, framebuffer output and Windows entry under an inspectable machine model. A result must be labeled “Windows on emulated Xbox” until reproduced on hardware.

The inspected xemu `v0.8.136` source uses PC-derived IDE/PIT/OHCI components and explicitly stubs the memory controller. Audit fidelity at the actual failing boundary. A PCI probe accepted by xemu may still be unsafe on hardware; a failure can also be an emulator limitation. [Pinned machine source](https://github.com/xemu-project/xemu/blob/fc24584ce88f0915ad7f04775bb7712c2e3f49ee/hw/xbox/xbox.c), [project description](https://xemu.app/docs/about/).

Physical Xbox testing must establish interrupt and timer behavior, DMA/cache coherence, RAM detection/reservations, ATA unlock/write integrity, OHCI input, encoder output, power/eject behavior and performance. A 128 MiB xemu setting does not establish stability of a hardware RAM upgrade. Fast desktop-host emulation is not a 733 MHz console benchmark.

The integration chat is currently using emulator resources. Future xemu work must use the project’s resource wrapper with private config, EEPROM, writable disks and monitor ports. Shared functional runs are not benchmarks. No emulator runs or builds were performed in this research round, and no additional chats or agents were started.

## Prerequisites and unresolved decisions

Paul supplies licensed **Windows 2000 Professional SP4 media first**, then the desired XP x86 service pack and Windows 98/SE editions, with applicable keys and permission to install the test instances. Preserve exact media/update hashes. XP needs an available authorized activation path where applicable. Keys remain outside reports and logs; no Windows images or keys were acquired.

Tool prerequisites are a compatible, privately staged FreeLoader/Cromwell build environment, the version-specific Windows driver toolchain/DDK and debugger/symbols where available, disk/image inspection tools and an independently backed-up writable target before storage tests. Existing nxdk can assist diagnostic XBE payloads; it does not replace the Windows HAL/driver toolchain. Use the shared environment as read-only infrastructure. A proprietary Xbox XDK or leaked Windows source is not a prerequisite. Retain and review licenses when reusing GPL ReactOS/Cromwell code and other components; distribute original adaptation source/build recipes separately from user-supplied Windows files.

Hardware prerequisites are the working authorized homebrew entry, a display/capture path and USB keyboard/mouse adapter. A retail Xbox lacks an ordinary COM port, so a conventional serial kernel debugger is not available by assumption. Early framebuffer breadcrumbs, emulator tracing and possibly a later hardware debug transport must be designed deliberately. UART additions, disk replacement, flash changes or RAM modification require their own plan and are not part of this round.

Outstanding decisions are the exact console revision/RAM, whether an already-upgraded unit exists, chosen Windows build and DDK, the FreeLoader merge base, the native boot-volume design, and how to observe failures before Windows input/network drivers exist. The highest technical uncertainties are safe Windows PCI enumeration after loader exit and binary compatibility of the adapted HAL/boot-video path. None is resolved merely by the Xbox’s NT-derived firmware.

## Project context and provenance

Read-only inputs were `PROJECT_STATUS.md`, `docs/roadmap.md`, `docs/parallel-work.md` and `docs/integration-fresh-029.md` in `C:\Users\Paul\Desktop\ogxbox-linux`, plus the homebrew-console-dev skill, its Xbox reference and `C:\Homebrew\environment-status.md`. Historical Linux hardware validation is accepted. Fresh029’s six final acceptance boots are emulator evidence for that Linux package. Existing-file-only FATX writing and the earlier Cromwell heap/initramfs overlap inform storage and reservation design; neither establishes Windows compatibility.

Relevant recorded Linux bases are `829b71ab17ed12e54be77cc31c76aec78aec3794` for the kernel and `9fc54d0c7cbed7bc3c70373642d833684853011f` for Cromwell, plus their documented patches. The shared nxdk revision is `58427c078b4ccb0121f359b6b6c536b3b2914976`. No branch, source map, shared plan or SDK was changed.

Sources were consulted on **2 October 2026** in the client timezone. Pinned repository dates are commit dates, not test dates. Microsoft KB links preserve Microsoft-authored documents on third-party archives: KB182751 was last reviewed 1 February 2005, KB314865 on 28 April 2005 and KB299340 on 4 June 2004. Mutable manuals/wiki pages have no verified publication revision here. The XboxDevWiki HOWTO was available through indexed content but direct retrieval timed out. ReactOS’s Xbox wiki was access-blocked, so official posts and source were used. The historical XP video description was indexed; the video was not independently inspected and is not native evidence.

The [provenance record](windows-on-original-xbox-provenance.json) records the source pins and context hashes. **Recommended next step:** perform N0’s FreeLoader merge/ABI audit and define the smallest native loader diagnostic payload, targeting Windows 2000 SP4. Then implement N1 in a separately authorized build/test round when emulator resources and the required media are available.
