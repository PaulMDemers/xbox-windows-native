# Windows 2000 Xbox: debugger exports and installed-volume reads

3 October 2026. The experimental HAL now supplies the six missing legacy debugger-port exports. All imports resolve between the installed Windows 2000 kernel, experimental Xbox HAL and boot-video module. **30 binary test groups pass. The 64 MiB Xbox emulator also reads and verifies eight files from the installed Windows NTFS disk. Windows has not entered its kernel in xemu or booted on the physical Xbox.**

This continues the [interrupt/timer checkpoint](../native-windows-nt5-interrupts/README.md). The installed PC disk remains a test fixture; its stock PC HAL has not been replaced.

## Changes and evidence

The new `KdPortInitialize`, `KdPortGetByte`, `KdPortPollByte`, `KdPortPutByte`, `KdPortSave` and `KdPortRestore` use the existing ReactOS direct 16450/16550 serial backend. Contracts were checked against the supplied installed kernel 5.0.2195.7376 and PC HAL 5.0.2195.6801. In particular, receive functions return status 0/1/2, and polling consumes a byte. Discovery and activation remain separate; an absent port fails without claiming a debugger connection.

The [11 new debugger test groups](kdport-tests.json) execute the built HAL and serial backend with modeled UART registers. They cover selection, baud validation, initialization, receive errors, the actual timeout loop, transmit waiting, save/restore and disconnection. Two actual installed-kernel receive helpers also execute through the new exports. Together with [11 synchronization checks](binary-unit-tests.json) and [eight interrupt-boundary checks](boundary-tests.json), this gives 30 passing groups against the saved final HAL.

This is a direct serial implementation. ARC firmware COM enumeration and modem command handling are absent. No physical UART or WinDbg session has been tested. The existing serial backend waits for a present transmitter to become ready. Instruction tests use synthetic machine state and do not establish real scheduling or interrupt delivery; EOI tests stop before IRET.

The [binding audit](installed-kernel-binding-audit.json) resolves 57 kernel-to-HAL imports, 10 kernel-to-boot-video imports, 81 HAL-to-kernel imports and nine boot-video-to-kernel imports. Name resolution is not runtime compatibility approval.

## Read-only Xbox emulator test

The final diagnostic starts through Cromwell ROM → FreeLoader → rosload, then reads the private snapshot of the installed NTFS disk. The previously tested UnleashX → Xromwell XBE route is a separate earlier checkpoint; it was not repeated here.

All eight files pass size and full-content checks: boot.ini, ntoskrnl.exe, hal.dll, bootvid.dll, SYSTEM, atapi.sys, disk.sys and ntfs.sys. Each also passes a zero-length read, an EOF read, a seek to seven bytes before EOF followed by a 32-byte request returning exactly seven bytes, verification of those seven bytes, and repeated EOF. The guest uses FNV-1a checksums; the [expected-file manifest](volume-expected-files.json) additionally records source SHA-256 hashes.

![All eight files pass in the 64 MiB Xbox emulator](evidence/nt5-volume-boundaries-001/frame-015.png)

This test exposed a real FreeLoader NTFS bug: reading at EOF returned an I/O error. The fix returns successful zero-byte reads for EOF and zero-length requests, and clamps requests to the logical file size. A zero-byte result from an underlying read before EOF still reports failure. The original failing probe and the intermediate successful probe remain as evidence.

The exact final ISO also rejects a blank Xbox disk at file 0 with open status 14, before reaching the success marker. [Negative-test screenshot](evidence/nt5-volume-boundaries-wrong-disk-001/frame-015.png).

Both final tests used 64 MiB, private disk copies and snapshot mode. The harness stopped its own emulator processes and removed staging disk copies. The Windows base disk's SHA-256 remains `59d7e920b19f10a05ba3a914f05c90e43764f2a7506a8bb16e816b781c54785e`. No physical Xbox disk was accessed. The normal loader and original Xbox HAL/boot-video targets also rebuilt successfully with diagnostics off for the normal loader.

## Remaining kernel-handoff work

The [boot-layout audit](boot-layout-comparison.json) matches 49 selected HAL offsets and 45 selected loader offsets against the exact kernel PDB. The loader parameter block is 104 bytes on both sides. The HAL TSS size and selected TSS fields match.

The loader extension still needs explicit review: Windows describes 40 bytes, the HAL compilation describes 76, and the normal loader compilation describes 124. The seven shared field offsets match, but the current loader reports its compiled size. This discrepancy is recorded, not assumed to be fatal or safe. Earlier whole KPRCB/KTHREAD size differences also remain outside the verified prefixes.

Next steps are to validate the native extension size and contents, inspect the installed SYSTEM hive's boot-driver selection against Xbox devices, finish remaining software-interrupt and BIOS-path checks, and add a halt immediately before the Windows kernel handoff to inspect the actual loader state. A traced kernel-entry experiment follows those checks. Storage, USB, display and other hardware drivers remain subsequent work. No additional ISO is needed now.

## Reproduction

Use private ReactOS source base `afc0127e8f937ab68503d715d948844973756aa1`, then apply patches 0005, 0006 and 0007 from the preceding checkpoints, followed by [0008 debugger ports](0008-nt5-debugger-ports.patch) and [0009 NTFS and volume diagnostic](0009-ntfs-volume-preflight.patch). The complete chain matches source tree `b6fb3f3be821ddb502a85f5c56d4af80177b4508`; [patch verification](patch-check.json) checks application, reverse checks for the two new patches, and whitespace. The private branch HEAD remains at the pinned base.

From the workspace root on this host:

```powershell
./outputs/native-windows-nt5-debug/Invoke-Build.ps1
C:/Python314/python.exe ./outputs/native-windows-nt5-debug/test-nt5-binary.py
C:/Python314/python.exe ./outputs/native-windows-nt5-debug/test-boundary.py
C:/Python314/python.exe ./outputs/native-windows-nt5-debug/test-kdport.py
C:/Python314/python.exe ./outputs/native-windows-nt5-debug/audit-nt5.py --kernel ./outputs/native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe --report installed-kernel-binding-audit.json --require-compatible
./outputs/native-windows-nt5-debug/Invoke-BootLayoutProbe.ps1
./outputs/native-windows-nt5-debug/Invoke-VolumeBuild.ps1
./outputs/native-windows-nt5-debug/Invoke-Regression.ps1
```

The audit option above enforces name binding only. Build scripts use the shared build lease and existing private RosBE toolchain. Tests require the task-local Python packages and earlier checkpoint scripts; the layout parser uses the matching Microsoft PDB already saved in work/symbols.

To package a newly built probe, use `make-volume-iso.py --freeldr <freeldr.sys> --rosload <rosload.exe> --output <fresh.iso>`. The final saved ISO is [volume-read-boundaries.iso](artifacts/volume-read-boundaries.iso). It contains diagnostics, not a Windows installation or a kernel-boot configuration.

Launch using the existing `outputs/native-windows-prebuild/Invoke-Diagnostic.ps1` with a fresh `-RunId`, `-Bios outputs/native-windows-build/artifacts/cromwell_1024.bin`, the diagnostic `-Iso`, `-HddSource outputs/native-windows-nt5/artifacts/windows2000-pc-base.qcow2`, and `-Seconds 45`. Omit HddSource for the blank-disk negative test. The helper owns the xemu lease, snapshots and cleanup. Do not run builds concurrently with an emulator test.

The [checkpoint](checkpoint.json) records verified outcomes and limitations. The [manifest](manifest.json) hashes this package. Run `C:/Python314/python.exe outputs/native-windows-nt5-debug/verify-checkpoint.py` to check saved-file integrity and report/artifact consistency. Screenshot observations are recorded explicitly; the verifier does not infer guest success from a host exit code.

Primary implementation reference: pinned [ReactOS cportlib](https://github.com/reactos/reactos/tree/afc0127e8f937ab68503d715d948844973756aa1/sdk/lib/cportlib). Native interface evidence is in [disassembly](kd-contracts-disassembly.txt) extracted from the supplied installed binaries, with [contracts and hashes](kd-contracts.json).
