# Native Windows pre-build engineering audit

**Subsequent binary evidence:** the [second-stage report](native-windows-stage2/README.md) adds seven unresolved HAL-to-kernel imports and compiled dispatch-layout differences. It also records successful UnleashX/Xromwell and second-stage diagnostics. The original source-level findings below remain historical context.

2 October 2026 audit; status updated 3 October 2026. **The first build and diagnostic emulator cycle has passed.** See the [build and test report](native-windows-build/README.md). The project is not ready to substitute the current ReactOS HAL into retail Windows or deploy to hardware. The findings below describe the pre-build audit; subsequent compilation and diagnostic evidence do not resolve the HAL compatibility issues.

## Source selection and bootstrap

Use the pinned NTATV ReactOS tree as the first implementation base. It already contains Xbox machine support, a Windows 2000 loader branch and the current framebuffer work. Of 13 directly compared Xbox platform/HAL files, eight are byte-identical to the pinned `binarymaster/reactos` Xbox branch; the differences include loader machine, console, disk, clock-reading and video code. This supports starting with one coherent tree rather than an immediate merge. It does not prove either tree builds or boots on the target. [NTATV tree](https://github.com/DistroHopper39B/reactos/tree/afc0127e8f937ab68503d715d948844973756aa1), [Xbox comparison tree](https://github.com/binarymaster/reactos/tree/7c35fc4ead884e1bd0640a9613f652c40bca8b2e).

The pinned Cromwell source has a purpose-built ReactOS/FreeLoader loader, including FATX and CD discovery, Multiboot header checking, hardware shutdown and transfer. It searches a CD for `/loader/freeldr.sys`, stages the file at `0x1000`, caps it at `0x80000` bytes, and transfers via the header-specified address. FreeLoader initially loads at `0x200000` and relocates to `0xF800`, with its embedded PE at `0x10000`. These constraints now have a host-side packaging validator. [Cromwell handoff source](https://github.com/PaulMDemers/cromwell/blob/9fc54d0c7cbed7bc3c70373642d833684853011f/boot/LoadReactOS.c), [FreeLoader Multiboot entry](https://github.com/DistroHopper39B/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/boot/freeldr/freeldr/arch/i386/multiboot.S).

Both sides use a historical memory-map representation: Cromwell points past the first size field, and FreeLoader consumes fixed 24-byte records beginning with the base address. Keep this producer/consumer pairing under test; do not silently substitute a generic Multiboot map parser. For 64 MiB, the intended gross regions are 60 MiB RAM plus 4 MiB framebuffer, followed by FreeLoader's own reservations. Cromwell shutdown lifetime, low-memory relocation and final NT allocations still need runtime validation.

The current Xbox memory detection writes test patterns at the 64 MiB boundary while probing for 128 MiB. That is another reason to validate the emulator path first and review the probe before physical deployment. The console's confirmed 64 MiB configuration should become an explicit hardware-path constraint.

## Concrete loader changes prepared

**Windows 2000 dispatch:** `ntldr/winldr.c` accepts `Windows2000`, but `bootmgr.c` lacks that entry and would reject it before reaching the NT loader. The patch adds the missing dispatch entry under the x86 guard. Using the generic `Windows` value would select the Server 2003 version path instead. The patch has now compiled successfully in both loader variants. Its Windows 2000 dispatch path has not been exercised at runtime.

**Diagnostic build:** a new opt-in `XBOX_NATIVE_PREFLIGHT` CMake option prints progress after platform, memory and boot-device initialization, dumps firmware descriptors, then halts before the second-stage loader. It is restricted to the Xbox x86 configuration. The production path is unchanged when this option is off.

**Two-stage packaging:** `freeldr.sys` loads `rosload.exe` from the boot root or `loader` subdirectory. This is required for the Xbox configuration in this tree. Following the Apple TV single-stage packaging would omit a required component. [Build and dispatch sources](https://github.com/DistroHopper39B/reactos/tree/afc0127e8f937ab68503d715d948844973756aa1/boot/freeldr/freeldr).

The Xbox console input routines still report no keyboard and block in `GetCh`. Do not design the first test around entering loader commands or acknowledging errors. The diagnostic terminates with a deliberate halt. Later automatic boot configuration and error capture must account for this.

## Actual Windows binary findings

The selected image's x86 UP kernel is `5.00.2195.6717`; its default HAL is `5.00.2195.6655`. Static PE inspection found:

| Relationship | Result |
| --- | --- |
| Windows kernel → supplied stock HAL | All 59 imported names exist |
| Supplied stock HAL → Windows kernel | All 125 imported names exist |
| Windows kernel → supplied boot-video interface | 10 imported names, all represented in the ReactOS bootvid specification |
| Windows kernel → current ReactOS HAL specification | Six imported names are absent |
| Current ReactOS x86 HAL forwarders → Windows kernel | Three referenced fast-mutex target names are absent |

The six missing HAL names are `KdPortSave`, `KdPortRestore`, `KdPortPollByte`, `KdPortInitialize`, `KdPortGetByte` and `KdPortPutByte`. Windows 2000 imports these directly from the HAL. Merely turning off kernel debugging does not remove the PE imports.

The three problematic forwarder targets are `ntoskrnl.ExiAcquireFastMutex`, `ntoskrnl.ExiReleaseFastMutex` and `ntoskrnl.ExiTryToAcquireFastMutex`. Those names do not exist in the selected Windows kernel's export table. A compatible HAL needs appropriate implementations or a verified alternative interface; inventing no-op replacements is not a solution. [ReactOS HAL export specification](https://github.com/DistroHopper39B/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/hal/hal.spec).

These are definite static blockers to a drop-in replacement, not an exhaustive list. The tree globally targets Windows 5.2-style headers, and its HAL checks PRCB version/build type and touches internal PCR/PRCB and dispatch structures. A compile-time export filter alone does not make those layouts Windows 2000-compatible. Build a candidate and inspect its complete imports/forwarders before attempting to load it, then validate calling conventions and structure accesses. [HAL initialization](https://github.com/DistroHopper39B/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/hal/halx86/generic/halinit.c).

The kernel entry RVA is `0xD1F0`, preferred image base `0x400000`, image size 1,718,784 bytes. Record the **actual relocated load base** before placing an entry breakpoint. The complete [binary audit JSON](windows-2000-binary-audit.json) contains hashes, PE metadata, imports and exports. Static symbol matches do not establish semantic or ABI compatibility.

## Hardware and storage boundaries

The Xbox HAL's PCI blacklist explicitly excludes dangerous host-bridge functions `0:0:1` and `0:0:2` and duplicate GPU slots on bus 1. The loader initializing the chipset does not guarantee that a stock Windows HAL or PCI driver will honor those restrictions later. Audit direct PCI accesses as well as HAL-mediated calls. [Xbox PCI handling](https://github.com/DistroHopper39B/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/hal/halx86/legacy/bus/pcibus.c).

FreeLoader includes FATX and Xbox partition support, and ReactOS's Xbox HAL includes partition adaptations. Retail Windows is not automatically supplied with either at runtime. The first diagnostic uses read-only CD payloads and a disposable emulator disk. The later installed system volume still requires a driver/layout design and an installed registry. The media's `SETUPREG.HIV` is a Setup hive, not a substitute for a completed installation's SYSTEM hive.

For boot video, the loader selects `xboxbvid.dll` for an Xbox identifier and loads it under the `bootvid.dll` module identity. Its exported names match the kernel's ten requirements, but its own imports and runtime assumptions still need a built-binary audit. A working boot display is separate from a desktop miniport/display driver.

## Readiness and corrections to earlier planning

**Completed:** pinned media and sources, initial patch, private branches, working RosBE cross-compiler, diagnostic and normal loader builds, Cromwell/Xromwell builds, real binary/media validation and three successful bounded diagnostic emulator boots.

**Later gates:** HAL compatibility implementation, actual Windows loader-block validation, a prepared installed fixture, boot-volume support, and a confirmed physical console revision. These do not prevent the first loader build and emulator diagnostic, but they do prevent a claim that Windows is ready to boot.

Do not assume that this tree accepts a literal `WindowsXP` boot type: the pinned file has an explicit `Windows2000` branch, but no literal `WindowsXP` branch. XP handling requires a separate version-path audit. Also, recognizing Windows 2000 in the NT loader was insufficient until its boot-manager dispatch entry was added.

The chosen RosBE archive is provided by the ReactOS project, and the project's release-engineering Dockerfile also uses RosBE-Unix 2.2.1. Its task-local build succeeded with GCC/G++ 15.2 and the recorded Ninja Python compatibility patch. The shared SDK was not modified. [Official archive](https://download.reactos.org/reactos/RosBE-Unix/2.2.1/), [upstream release-engineering recipe](https://github.com/reactos/Release_Engineering/blob/master/Dockerfile).
