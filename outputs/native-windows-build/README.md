# Native Xbox Windows project: first build and emulator results

3 October 2026. **The initial Cromwell → FreeLoader diagnostic gate passed on three independent 64 MiB xemu cold boots.** The toolchain and both diagnostic and normal loader variants are built. Windows itself has not been entered.

![Diagnostic completion and memory map](evidence/preflight-001/frame-015.png)

## What ran successfully

The private RosBE 2.2.1 toolchain built with host GCC/G++ 15.2.0. It supplies target GCC 8.4.0, CMake 3.17.2-ReactOS and Ninja 1.10.0. The only additional source compatibility change was replacing Ninja's removed Python `pipes.quote` with `shlex.quote`. The original archive, derived archive hashes and patch are retained in the [build kit](../native-windows-prebuild/README.md). The first bootstrap attempt stopped at RosBE's non-root prompt; the wrapper now supplies its confirmation for the private install prefix. The subsequent bootstrap completed.

The pinned ReactOS tree compiled `freeldr.sys` and `rosload.exe` with the Xbox target and the diagnostic flag enabled. A separate build with that flag disabled produced the normal loader. Cromwell and Xromwell compiled with GCC 12.5.0 and the full legacy heap reservation correction. Build logs retain upstream compiler and make warnings; these were successful builds, not warning-free builds.

The emulator booted the new Cromwell ROM and loaded `/loader/freeldr.sys` from our diagnostic ISO. Each run used a fresh private EEPROM copy, private blank disk, snapshot mode, disabled networking and explicit 64 MiB RAM. Each guest was stopped after its bounded run and its scratch overlay was removed. The common integration helpers held the appropriate build or emulator lease. Shared development sources and the user's dashboard disk were not modified.

| Observation | Result |
| --- | --- |
| Xbox platform initialization | XWN10 on all three boots |
| Loader memory initialization | XWN20 on all three boots |
| Boot-device initialization | XWN30; `multi(0)disk(0)cdrom(96)` |
| Diagnostic completion | XWN40 on all three boots |
| CPU stop | `HLT=1`, `EIP=0x10776`, matching the instruction immediately after the diagnostic `hlt` |
| Repeatability | Identical framebuffer bytes and input hashes on all three boots |
| Diagnostic ISO readback | Extracted FreeLoader bytes exactly match the validated build |

The unusual CD index 96 is the existing loader's representation of Cromwell's `0xE0` CD boot-device number. It does not identify 96 physical drives. Device initialization alone does not prove that FreeLoader can subsequently read Windows files.

## Memory review

The seven displayed firmware descriptors cover exactly 64 MiB, with no gaps or overlaps. Addresses below are half-open ranges; the end is excluded.

| Physical range | Type |
| --- | --- |
| `0x00000000–0x00001000` | Free |
| `0x00001000–0x00008000` | Firmware temporary |
| `0x00008000–0x0000F000` | Loader stack |
| `0x0000F000–0x0004F000` | Loaded program |
| `0x0004F000–0x0005F000` | Firmware temporary / disk read buffer |
| `0x0005F000–0x03C00000` | Free |
| `0x03C00000–0x04000000` | Firmware permanent / framebuffer |

The framebuffer is excluded from free memory, and the observed loader and stack addresses sit in reserved ranges. The first page is marked free by this source. Review its treatment before an NT handoff. This diagnostic shows the firmware discovery map; it does not certify the allocator's later state or the final NT loader-block map. [Machine-readable review](evidence/memory-map.json).

## Saved artifacts

- [Diagnostic FreeLoader](artifacts/freeldr.sys) and [test ISO](artifacts/xwn-preflight-001.iso): stop at XWN40 before the second stage.
- [Cromwell ROM](artifacts/cromwell_1024.bin): tested in xemu, with generic CD autoboot enabled. This is not a hardware flash instruction.
- [Xromwell XBE](artifacts/xromwell.xbe): built, but its UnleashX launch path has not been tested.
- [Normal FreeLoader](artifacts/normal/freeldr.sys) and [normal second-stage loader](artifacts/normal/rosload.exe): built and statically validated; no runtime test yet.
- [Test results](test-results.json), [artifact hashes](manifest.json), [loader validation](evidence/loader-validation.json), [halt disassembly](evidence/diagnostic-halt-disassembly.txt), and complete logs/evidence alongside this report.

To repeat the diagnostic from the workspace in PowerShell 7.4+, choose a fresh run ID:

```powershell
./outputs/native-windows-prebuild/Invoke-Diagnostic.ps1 `
  -RunId preflight-004 `
  -Bios ./outputs/native-windows-build/artifacts/cromwell_1024.bin `
  -Iso ./outputs/native-windows-build/artifacts/xwn-preflight-001.iso `
  -Seconds 60
```

## Next development gates

1. Extend diagnostics to verify file reads and the second-stage handoff, then reproduce the chain through Xromwell on a private UnleashX fixture. A Cromwell ROM boot does not establish the softmod launch path.
2. Implement and audit a Windows 2000-compatible Xbox HAL. The current ReactOS HAL has six missing imported names and three incompatible fast-mutex forwarders, in addition to unresolved internal structure compatibility. See the [binary audit](../native-windows-prebuild-audit.md).
3. Prepare an installed Windows system volume and registry, with an explicit boot-storage driver and partition strategy. Validate the actual Windows loader block, memory reservations and boot-video interface before entering the kernel.
4. Trace the Windows kernel at its actual relocated entry address. Only then expand into interrupt/timer, storage, USB input and video-driver bring-up.

The supplied **`EN_WIN2000_PRO_SP4.ISO` is sufficient for the next Windows 2000 work; no additional ISO is required now.** The other supplied image remains a secondary comparison image. Physical console revision, recovery arrangements and a separate test disk remain preflight items for hardware deployment.
