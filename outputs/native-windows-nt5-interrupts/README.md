# Windows 2000 Xbox HAL: interrupt and timer adapters

3 October 2026. The experimental HAL now has Windows 2000 adapters for interrupt return, timer entry, interrupt completion and DPC dispatch. **All 81 HAL imports resolve against the installed Windows 2000 kernel.** The reverse direction still lacks six debugger-port exports. **Windows has not booted in xemu or on the Xbox.**

This checkpoint builds on the [installed 64 MiB PC fixture and first NT5 HAL](../native-windows-nt5/README.md). That disk and the previously verified UnleashX → Xromwell → FreeLoader → rosload route are unchanged.

## Changes

- Interrupt return now resets ESP and EBP to the saved trap frame before jumping to Windows `Kei386EoiHelper`. It no longer imports the ReactOS-specific `KiEoiHelper`.
- Timer entry translates the C arguments into the native Windows contract: increment in EAX, trap pointer in EBP, and old IRQL plus interrupt vector on the stack. Windows performs the time update and completes the interrupt.
- The public `HalEndSystemInterrupt` entry translates Windows' vector argument into the trap pointer expected by the internal PIC implementation. Internal HAL callers retain their original interface.
- DPC dispatch preserves C nonvolatile registers around Windows' assembly helper, which can clobber EBX.
- Trap entry uses the Windows 2000 PCR debug-active byte at offset `0x50`, avoiding the incompatible newer `KTHREAD.Header.DebugActive` field. User/V86 debug-register save and kernel-register restore use verified PRCB offsets.
- HAL initialization no longer reads the ReactOS-specific loader-extension tail in the NT5 build.

These changes are isolated to the opt-in NT5 target. The original ReactOS Xbox HAL and boot-video targets also rebuild successfully.

## Verification

**19 test groups pass against the final built HAL:** the prior 11 mutex/dispatch/spinlock checks and [eight interrupt-boundary groups](boundary-tests.json).

The new tests check stack layout, register preservation, argument translation, trap/debug state and exception-chain restoration. They also execute the actual supplied **5.0.2195.7376** kernel's timer and EOI instructions using synthetic machine state. One path exercises 64-bit time carry. Another starts at the built HAL IRQ0 assembly entry, passes through its C clock handler and Windows time update, and reaches the instruction immediately before `IRET`. Both accepted and spurious IRQ0 cases pass.

The interrupt-controller begin/end operations are mocked. Tests stop **before executing `IRET`**; they do not establish real interrupt delivery, scheduler/APC correctness, user-mode return, timer expiry/DPC processing, PIC behavior or a kernel boot. The actual-kernel timer case selects an empty timer list without a tick rollover. Debug-register entry is tested separately for kernel, user and V86 cases.

The compiled layout probe matches **55 selected field offsets** against the exact kernel's public PDB, including trap fields, PCR interrupt state, processor prefixes and saved debug registers. [Comparison](layout-comparison.json). Whole KPRCB/KTHREAD sizes still differ; this is not a complete ABI audit. BIOS/TSS paths, remaining inlined accesses, software interrupts and loader structures still require review.

[Binary evidence](boundary-disassembly.txt) was extracted from the supplied installed kernel and PC HAL. The source-side interface discrepancy is also visible in the upstream [ReactOS export specification](https://github.com/reactos/reactos/blob/afc0127e8f937ab68503d715d948844973756aa1/ntoskrnl/ntoskrnl.spec). The disassembly windows include adjacent code and are evidence windows, not recovered source functions.

## Remaining boot gates

The [binding audit](installed-kernel-binding-audit.json) still fails for `KdPortInitialize`, `KdPortGetByte`, `KdPortPollByte`, `KdPortPutByte`, `KdPortSave` and `KdPortRestore`. No placeholder implementations were added merely to satisfy imports.

Next implement and test the legacy debugger-port interface, finish the remaining ABI checks, then validate loader reads and the boot configuration from the installed Windows volume. A traced xemu kernel handoff comes after those gates. PCI/storage driver selection remains separate work. No additional ISO is needed now.

## Reproduction and saved artifacts

Use the pinned private source base `afc0127e8f937ab68503d715d948844973756aa1` and apply these patches in order:

1. [0005 native I/O](../native-windows-prebuild/patches/0005-native-io-cumulative.patch)
2. [0006 initial NT5 HAL](../native-windows-nt5/0006-nt5-hal-experimental.patch)
3. [0007 interrupt boundary](0007-nt5-interrupt-boundary.patch)

Patch 0007 is incremental. The complete chain applies to the pinned base, matches the current private source tree, and passes whitespace and reverse-application checks. [Patch verification](patch-check.json). The source branch remains at the pinned base; the patches capture the changes.

On this host, from the workspace root:

```powershell
./outputs/native-windows-nt5-interrupts/Invoke-Build.ps1
./outputs/native-windows-nt5-interrupts/Invoke-LayoutProbe.ps1
C:/Python314/python.exe ./outputs/native-windows-nt5-interrupts/compare-layouts.py
C:/Python314/python.exe ./outputs/native-windows-nt5-interrupts/test-nt5-binary.py
C:/Python314/python.exe ./outputs/native-windows-nt5-interrupts/test-boundary.py
C:/Python314/python.exe ./outputs/native-windows-nt5-interrupts/audit-nt5.py --kernel ./outputs/native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe --report installed-kernel-binding-audit.json --require-compatible
```

The final command is expected to fail while the six debugger exports are absent. Build scripts hold the shared build lease and use the existing private RosBE toolchain. Python dependencies are the task-local packages recorded in the previous checkpoint. The structure parser uses the previously downloaded matching Microsoft PDB.

The new HAL and boot-video binaries are in [artifacts](artifacts/). Tests derive private function addresses from the final PE's symbol table. Reports record the tested hashes; [manifest](manifest.json) hashes the saved deliverables. Build logs include the initial missing-field compile failure and its fix, the successful final build and original-HAL regression build. No VM was launched for this checkpoint.
