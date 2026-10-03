# Windows 2000 Xbox: verified halt before kernel entry

3 October 2026. **The 64 MiB Xbox emulator now runs the full loader path, loads the Windows kernel and experimental Xbox HAL, binds 1,673 imports across 21 modules, prepares paging, and halts immediately before calling the kernel.** All 15 selected boot drivers load. Windows kernel execution, driver initialization and a Windows boot remain untested.

This continues the [debugger and NTFS checkpoint](../native-windows-nt5-debug/README.md). The unchanged experimental HAL carries its earlier 30 passing binary test groups; those tests were not rerun here because the HAL binary did not change.

## What changed

For Windows 2000 on x86, FreeLoader now reports a 40-byte loader extension ending at `TriageDumpBlock`, matching the exact installed kernel's PDB. The allocation stays large enough for loader-private fields. Other OS selections retain their existing size. A compile-time assertion checks the final native field offset, and the guest record verifies the actual size and version at handoff.

The opt-in `XBOX_NATIVE_NT5_HANDOFF` diagnostic follows Cromwell ROM → FreeLoader → rosload → the Windows loader routines. It reads the installed NTFS fixture and loads the experimental `halxboxnt5.dll` and `xboxbvid.dll` from the diagnostic CD. The installed disk's stock HAL, registry and drivers remain unchanged. The previously verified UnleashX/Xromwell XBE route was not repeated in this checkpoint.

The diagnostic halts before `KiSystemStartup` regardless of validation outcome. Its success record is written after page-table switching and list conversion. It never enables kernel entry. The ordinary loader target has this option off.

## Runtime evidence

The [final state inspection](evidence/nt5-handoff-006/state-030.json) was captured through our emulator monitor with the guest paused. The inspector walks actual guest page tables, checks list backlinks, resolves mapped import tables against mapped exports, and compares executable sections against the supplied source binaries after expected relocation and import-binding edits.

| Check | Result |
|---|---|
| RAM configured | 64 MiB |
| CPU | Halted, paging enabled (`CR0=0x80010033`) |
| Page-directory address | `0x028ea000` |
| Intended kernel entry | `0x823cee10`, not called |
| Loader extension | 40 bytes, version 5.0 |
| SYSTEM hive | 1,810,432 bytes, mapped and identified as a registry hive |
| Loaded modules | 21 |
| Selected boot drivers | 15, each linked to a loaded module |
| Memory descriptors | 23, linked list valid |
| Import addresses checked | 1,673, all equal expected exports |
| Executable-section comparison | Kernel, HAL and boot-video match after expected loader edits |
| Boot path | `multi(0)disk(0)rdisk(0)partition(1)\WINNT\` |

All three NLS pointers are mapped. A separate cold run (`nt5-handoff-003`) also reached the same successful pre-entry state; the later final run adds full import-address and executable-section verification. The two captures within the final run describe the same halted guest, not two separate boots.

The first diagnostic printed after paging and faulted on the now-unmapped framebuffer at `0x03c00000`, eventually causing a triple fault. The revised diagnostic uses a monitor-readable memory record after paging and does not touch the framebuffer. Earlier failing runs and the CPU trace are retained. The final black framebuffer is expected after machine preparation; success comes from the decoded record and machine state, not a screenshot or host process exit code.

Two intermediate inspection attempts also exposed assumptions in the host verifier: FreeLoader converts import lookup entries from RVAs to virtual addresses, and the Windows 2000 kernel keeps import tables inside an executable section. The verifier now accounts for exactly those loader edits and checks the remaining executable bytes. These were verifier failures after the guest reached its intended halt.

The normal loader and original Xbox HAL/boot-video regression targets build successfully. All normal-loader diagnostic flags are off. Builds and xemu runs used separate shared-resource leases. Emulator processes, snapshot storage and staging disk copies were cleaned up; temporary 64 MiB memory captures were decoded and deleted. The base Windows disk hash is unchanged.

## Boot-driver findings and next work

The [read-only SYSTEM audit](boot-driver-audit.json) selects ControlSet001 and 15 services. NTFS has Start=4, but the pinned loader explicitly adds the boot filesystem driver, so it is present in the actual loaded list. Group/tag ordering in the static report is preliminary; the guest list includes dependency ordering.

The fixture enables IntelIde for its PC controller and disables PciIde. It has no critical-device entry for the Xbox IDE controller, whose device ID is `01BC`. See the hardware team's [Xbox hardware overview](https://xboxdevwiki.net/Xbox_Hardware_Overview). Loading these driver images proves that files and imports are available; it does not establish that the PC storage stack can drive the Xbox controller.

The next kernel experiment should trace entry and stop at early initialization boundaries, with particular attention to remaining HAL software-interrupt paths, BIOS assumptions and PCI enumeration. Then prepare a separate disposable storage configuration for the Xbox IDE controller and test driver initialization there. Do not treat this PC registry configuration as a ready hardware installation. The existing OEM-font substitution in FreeLoader and the previously recorded whole-structure ABI differences also remain to be reviewed. No additional ISO is needed now.

## Reproduction

Apply patches 0005–0009 from the preceding checkpoints to private source base `afc0127e8f937ab68503d715d948844973756aa1`, then apply [0010](0010-nt5-loader-extension-handoff.patch). [Patch verification](patch-check.json) confirms the full chain matches source tree `efa06f9206e64a6b6a4df96ecab674247858edae`, including reverse and whitespace checks. The private branch HEAD remains pinned to the original base.

From the workspace root on this host:

```powershell
./outputs/native-windows-nt5-handoff/Invoke-Build.ps1
C:/Python314/python.exe outputs/native-windows-nt5-handoff/audit-boot-drivers.py
C:/Python314/python.exe outputs/native-windows-nt5-handoff/extract-layouts.py
C:/Python314/python.exe outputs/native-windows-nt5-handoff/make-iso.py --output outputs/native-windows-nt5-handoff/artifacts/fresh-handoff.iso
./outputs/native-windows-nt5-handoff/Invoke-Diagnostic.ps1 -RunId fresh-handoff-001 -Bios outputs/native-windows-build/artifacts/cromwell_1024.bin -Iso outputs/native-windows-nt5-handoff/artifacts/fresh-handoff.iso -HddSource outputs/native-windows-nt5/artifacts/windows2000-pc-base.qcow2 -Seconds 45
./outputs/native-windows-nt5-handoff/Invoke-Regression.ps1
```

Use fresh ISO and run names. The scripts reuse the private RosBE toolchain, existing HAL artifacts, task-local Python packages, installed fixture and matching PDB. The final saved diagnostic is [handoff-002.iso](artifacts/handoff-002.iso). It includes no Windows binaries and cannot call the kernel in this build. Do not deploy it as a Windows bootloader to the physical Xbox.

[Checkpoint](checkpoint.json) records outcomes and [manifest](manifest.json) records package hashes. `C:/Python314/python.exe outputs/native-windows-nt5-handoff/verify-checkpoint.py` checks saved artifact/report consistency. The decoder uses exact PDB offsets for loader blocks and module entries; boot-driver and memory-descriptor layouts are from the pinned loader source and are not a completed native-kernel ABI audit.
