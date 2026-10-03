# Windows 2000 Xbox development: first NT 5.0 HAL target

3 October 2026. **Windows 2000 boots to its desktop in the 64 MiB PC fixture with the installation media detached.** The experimental Xbox HAL also builds, and 11 tests pass against its actual x86 instructions. That HAL is still incompatible with Windows at the interrupt boundary and is not ready for an Xbox kernel boot. The previously verified UnleashX → Xromwell → FreeLoader → rosload route remains the loader baseline.

## Implemented

The new opt-in `XBOX_NT5_HAL` target builds `halxboxnt5.dll` separately from the existing ReactOS HAL. It requires an i386 Release build and selects the Windows 2000 header contract. The original target retains its existing version settings.

- Public/private dispatch versions are now **2 / 1**, with checked sizes **68 / 48 bytes**. The NT5 target does not register the newer debugger callbacks beyond the private table's end.
- Fast mutexes are implemented inside the HAL with acquire, wait, wake, try-acquire and IRQL restoration behavior. The three unresolved `Exi*` forwarders are gone.
- Four disk/drive-letter exports now call the Windows kernel's existing dispatch callbacks. The supplied stock HAL confirms stdcall exports converting to fastcall callbacks at offsets `0x18`, `0x1C`, `0x20`, and `0x24`. Existing Xbox partition hooks remain in that path.
- The DMA bitmap operation uses the available `RtlClearBits(..., 1)` interface. Free uniprocessor queued-lock attempts use IRQL exclusion consistently with the existing UP acquire/release implementation, eliminating the newer kernel helper dependency.
- The NT5 HAL's native PE version is 5.0. It is an audit/development artifact, not an approved replacement for an installed HAL.

The binary tests execute the built mutex, disk-wrapper and queued-lock instructions in Unicorn. Kernel services and interrupt-level changes are mocked; a contended wait simulates one owner release. They check argument forwarding, return values, stack cleanup, preserved registers, mutex count/owner, wait/wake calls and restored IRQL. **They do not test the Windows scheduler, interrupt hardware, concurrency or a kernel boot.** [Test results](binary-unit-tests.json).

The original Release ReactOS `halxbox` and `xboxbvid` targets also rebuild successfully after the shared-source changes. Patch application and whitespace checks pass. Verification in this checkpoint covers builds, binary routine tests and the PC installation. The new HAL has not been executed in xemu or on a physical console.

## Remaining compatibility work

| Binding direction | Before | Current |
| --- | --- | --- |
| HAL → Windows kernel | Seven missing imports | `KiEoiHelper` remains |
| HAL fast-mutex forwarders | Three unresolved | None |
| Windows kernel → HAL | Six missing legacy debugger-port exports | All six remain |

The six debugger names are `KdPortInitialize`, `KdPortGetByte`, `KdPortPollByte`, `KdPortPutByte`, `KdPortSave` and `KdPortRestore`. Boot-video import/export names continue to resolve. The [binding gate](binary-audit.json) still deliberately fails. The updated kernel in the other supplied ISO has the same outstanding names. [Alternate-media audit](alternate-media-audit.json).

Import names understate the remaining work. Inspection of the supplied Windows binaries confirms that `Kei386EoiHelper` consumes a trap frame through ESP and EBP. The inherited ReactOS `KiEoiHelper` interface takes a C argument. Windows `KeUpdateSystemTime` consumes its increment in EAX, whereas the current ReactOS fastcall declaration passes it in EDX. These require verified assembly adapters and review of the surrounding entry/exit paths, not a symbol rename. [Recorded binary evidence](stock-contracts-disassembly.txt).

Microsoft's public server supplied the matching DBG/PDB identity for the OEM media's 5.0.2195.7376 kernel. The DBG timestamp/image size and referenced PDB signature/age were checked. The older stock kernel and HAL DBG requests returned 404. [Retrieval provenance](kernel-symbols.json); [Microsoft symbol-server documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/microsoft-public-symbols).

The PDB types were compared with constants compiled using the actual new HAL flags:

| Layout | Microsoft 2195.7376 | Compiled HAL |
| --- | ---: | ---: |
| `FAST_MUTEX` size | 32 | 32 |
| `KTRAP_FRAME` size | 140 | 140 |
| Trap EIP / EFLAGS / exception-list offsets | 104 / 112 / 76 | Match |
| PRCB current-thread / build-type offsets | 4 / 18 | Match |
| `KPRCB` size | 2544 | 3796 |
| `KTHREAD` size | 432 | 440 |
| Thread debug flag used by interrupt entry | 44 | 3 (`Header.DebugActive`) |

Changing `NTDDI_VERSION` does not fix those inherited thread/processor structures. Audit every direct access in the interrupt, APC/DPC, timer, BIOS and processor-init paths. Matching prefix fields alone do not establish compatibility. [Full selected Microsoft layouts](microsoft-kernel-layouts.json), [compiled constants](hal-layout-probe.json), [comparison](abi-comparison.json).

The next native milestone is a separately tested NT5 interrupt/timer boundary and legacy debugger-port backend, followed by loader-block and boot-volume validation. Only then should a traced Windows kernel handoff be attempted in xemu. Physical deployment still needs the Xbox hardware revision and a recovery/test-disk arrangement.

## Build and verification

Source base: ReactOS `afc0127e8f937ab68503d715d948844973756aa1`. Apply the earlier `0005-native-io-cumulative.patch`, then [0006-nt5-hal-experimental.patch](0006-nt5-hal-experimental.patch). Unlike patch 0005, patch 0006 is incremental. It does not include the loader diagnostic changes.

```powershell
./outputs/native-windows-nt5/Invoke-Build.ps1
./outputs/native-windows-nt5/Invoke-LayoutProbe.ps1
C:/Python314/python.exe ./outputs/native-windows-nt5/test-nt5-binary.py
C:/Python314/python.exe ./outputs/native-windows-nt5/audit-nt5.py --require-compatible
```

The last command is expected to fail until the remaining bindings are implemented. The first two commands use the shared build lease and private pinned RosBE toolchain. Binaries are under `artifacts/`; build logs, patch checks and test reports are retained alongside this report.

## PC fixture

The private PC fixture uses QEMU 10.2.1, Pentium III emulation, one CPU, **64 MiB**, legacy IDE, a 2 GiB disk, Cirrus video, ACPI/HPET disabled and no network interface. QEMU and needed packages were extracted into this task's toolchain directory; the host package database and shared console SDKs were not modified. [Runtime provenance](runtime-provenance.json).

`EN_WIN2000_PRO_SP4.ISO` identifies retail-channel setup. It reached graphical setup but rejected the product ID present in the other ISO. The supplied `Windows 2000 (SP4).iso` identifies OEM-channel setup and accepted its own included product ID. No licensing files were patched and no external product key was obtained. The key remains confined to the supplied media and private setup fixture; reports contain a redacted answer-file example.

The initial answer floppy omitted `EncryptedAdminPassword=No`, so the OEM run required confirmation of a blank Administrator password. The answer-generator script now specifies the blank-password form and encryption setting explicitly; that unattended correction has not been tested in a fresh installation.

## Installed fixture checkpoint

![Disk-only Windows 2000 desktop at 64 MiB](pc-evidence/disk-only-001.png)

The OEM installation completed. A subsequent cold launch with **no CD image or setup floppy attached** reached the desktop. Windows was then shut down through its own menu and displayed “It is now safe to turn off your computer” before the owned QEMU process was stopped. [Shutdown evidence](pc-evidence/clean-shutdown.png).

Twenty-five installed boot/configuration files were extracted read-only. The SYSTEM hive's sequence numbers match, `SystemSetupInProgress=0`, and `SetupType=0`. Its installed kernel is **5.0.2195.7376**, byte-identical to the audited OEM-media kernel. The installed PC HAL is **5.0.2195.6801**; boot video is **5.0.2172.1**. [Installed-system audit](installed-system-audit.json), [extracted-file hashes](pc-extraction.json), [candidate HAL binding against the installed kernel](installed-kernel-binding-audit.json).

The disk has one active NTFS partition starting at LBA 63. The hive selects boot-start Atapi, IntelIde, Pci and Disk services. PciIde, Ntfs and Fastfat have `Start=4` in this particular installation, despite the successful NTFS boot. The native loader's filesystem loading and the Xbox controller's driver selection still need deliberate verification; the PC storage configuration is not an Xbox driver configuration.

The compressed [PC base disk](artifacts/windows2000-pc-base.qcow2) is a reusable reference. Its logical contents were compared with the installed disk, then with a new writable overlay. Both comparisons passed. The task's harness uses that small overlay for further runs. [Base-image hash and retention record](pc-base-image.json).

Run the installed fixture on this host with:

```powershell
wsl -d Ubuntu -- python3 /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5/pc-fixture.py launch --disk-only --minutes 20
```

The harness is headless and owns its QEMU process until exit or its time limit. In another terminal, its `capture --name screen` action saves a PNG; `key --keys ctrl-esc` sends a guest key sequence, and `stop` stops only this private instance. Interactive use of a separate QEMU frontend should use a writable copy or overlay of the base disk. The local Administrator password is blank for this isolated development fixture.

**No additional ISO is needed for the next development checkpoint.** This PC VM supplies an installed Windows volume and registry hive; it is not evidence of Windows running on Xbox hardware. Continue with verified NT5 interrupt/timer adapters, then native-loader reads from this installed volume before attempting kernel execution.
