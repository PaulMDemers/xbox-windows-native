# Native Windows pre-build package

**Latest checkpoint, 3 October:** the [second-stage report](../native-windows-stage2/README.md) records verified CD reads, two negative tests, two successful UnleashX/Xromwell launches, and compiled debug/release HAL audits. Use `-Stage io`, `-Stage hal-audit` or `-Stage hal-free-audit` for those builds. The cumulative ReactOS patch 0005 replaces patch 0001 for fresh source preparation. Windows kernel entry remains untested.

Prepared 2 October 2026; updated 3 October 2026 for Paul's 64 MiB original Xbox, softmodded with UnleashX and a previously working Xromwell launch path.

**First build and diagnostic cycle completed.** RosBE, diagnostic and normal FreeLoader/rosload, Cromwell and Xromwell built successfully. Three isolated 64 MiB xemu cold boots reached XWN40 with identical output and the expected halted CPU. See the [build and test report](../native-windows-build/README.md) for binaries, evidence and limits. Windows installation and kernel entry have not been attempted.

This package prepares native Xbox development. WSL is a host build environment. xemu is a development test machine. Windows on the physical Xbox remains the deployment target.

## What is staged

- Independent native WSL Git clones under `/home/paul/xbox-windows-native/sources`, on `codex/native-windows-preflight`, with no Git alternates. The ReactOS and Cromwell patches are applied and remain visible as working-tree changes.
- Complete, pinned Windows-side source checkouts under this task's `work/reference-sources` for read-only comparison.
- RosBE-Unix 2.2.1 source extracted under the private native root; archive and hash retained. Missing Texinfo/Perl utilities are extracted task-locally, and `python` is a task-local link to the installed Python 3. System packages and compiler defaults were not changed.
- [Source/input lock](sources.lock.json), [initial patch](patches/0001-win2000-dispatch-and-preflight.patch), [source comparison](source-comparison.json), and the copied Cromwell heap-reservation patch.
- The [binary audit](../windows-2000-binary-audit.json) and [engineering findings](../native-windows-prebuild-audit.md).

The implementation base is `DistroHopper39B/reactos` at `afc0127e8f937ab68503d715d948844973756aa1`, built with `ARCH=i386`, `SARCH=xbox`, `OARCH=pentium`. Keep the other Xbox branch as a reference rather than beginning with a broad merge.

## First build sequence

For a fresh prepared environment, these are the sequential stages in PowerShell 7.4+. They have already completed in this workspace; the toolchain and Cromwell scripts deliberately refuse to overwrite existing destinations.

```powershell
./Invoke-Build.ps1 -Stage toolchain
./Invoke-Build.ps1 -Stage diagnostic
./Invoke-Build.ps1 -Stage cromwell
```

The wrapper holds the integration project's cooperative `build` lease. A busy lease is a reason to retry later; it is not permission to interrupt another task. All destinations belong to this task. All four stages have run successfully, including the separate `loader` stage.

The toolchain stage builds RosBE into `/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1`. Its local builder uses four jobs and limited CPU affinity. It succeeded with the installed GCC/G++ 15.2 host pair. `patch-ninja-python.py` updates the private Ninja archive to use `shlex.quote`, because Python 3.14 no longer includes `pipes`; the original is retained and [archive hashes](ninja-archive-provenance.json) are recorded. A failed partial toolchain directory is deliberately not overwritten automatically. Downloaded host package versions and hashes are in [host-packages.lock.json](host-packages.lock.json).

The diagnostic stage builds **both `freeldr` and `rosload`**. The Xbox path in this tree uses two loader stages, even though the Apple TV path does not. The diagnostic `freeldr.sys` stops before launching `rosload.exe`; building both exposes dependency/build issues early.

The Cromwell stage builds a private ROM and Xromwell XBE with the known heap-reservation correction. It enables the upstream generic CD detection path through `XBOX_LINUX_AUTOBOOT_CD`; the diagnostic disc contains only FreeLoader and no Linux guest. It omits the Linux project's FATX Linux-autoboot flags. The Cromwell upstream `all` target includes cleanup, so this recipe runs it without parallel make.

Expected artifacts:

```text
/home/paul/xbox-windows-native/build/diagnostic/boot/freeldr/freeldr/freeldr.sys
/home/paul/xbox-windows-native/build/diagnostic/boot/freeldr/freeldr/rosload.exe
/home/paul/xbox-windows-native/build/cromwell/image/cromwell_1024.bin
/home/paul/xbox-windows-native/build/cromwell/xbe/xromwell.xbe
```

Confirm actual artifact locations and capture complete logs, compiler versions, source/patch hashes and binary hashes after the build. A target's successful compilation is not a boot test.

## Package the diagnostic test disc

After the diagnostic binary exists, run `validate_loader.py` against it. Then use `make_diagnostic_iso.py --freeldr <built-freeldr.sys> --output <fresh-task-ISO-path>` with the existing Windows Python. Windows can read the WSL artifact through `\\wsl.localhost\Ubuntu\home\paul\xbox-windows-native\...` or an explicitly copied, hash-verified task artifact.

The packager creates a conventional ISO9660 disc with `/loader/freeldr.sys`, which Cromwell's ReactOS loader searches for. This first disc contains no Windows binaries and does not need El Torito boot code: Cromwell loads the file itself. It is for the **Cromwell ROM emulator test**, not an Xbox game-disc launcher. A later UnleashX/Xromwell test needs its own XBE/FATX packaging.

The validator checks the pinned chain's 512 KiB file limit, Multiboot checksum/location/address mapping, x86 PE format, entry bounds and low-memory image extent. It is a packaging gate, not a full proof of runtime memory safety.

## First xemu test

`Invoke-Diagnostic.ps1` now implements this procedure and passed three runs. Prepare one fresh task-owned run directory per boot. Copy the existing 256-byte EEPROM and the small preserved blank `C:\Emulators\xemu\system\xbox_hdd.qcow2` into it. Use the private copies as writable inputs; do not use the configured 1 GiB working dashboard disk. Keep MCPX read-only at its existing path.

Use the pinned patched xemu executable recorded in `sources.lock.json`. Its current SHA-256 matches its adjacent provenance record. Launch inside `with_xbox_resource.ps1 -Resource xemu -Shared` through `start_xemu_instance.ps1`, using task ID `windows-native`, a private config, private run/scratch paths, `-m 64`, `-snapshot`, the new diagnostic disc and newly built Cromwell ROM. Configure disabled update checks. Check that the selected localhost monitor port is unused; **4574 is a proposed port, not a reserved resource**. Bind monitor/debug services to localhost only.

The helper owns the task-specific process identity. Hold the lease until that process exits, stop only its PID, and call `complete_xemu_instance.ps1` in `finally` afterward. Use the separate UI lease for window capture or foreground input. Shared-run timing is not benchmark evidence. [xemu command-line reference](https://xemu.app/docs/cli/).

Do not claim that a ROM-started xemu result proves the softmod/XBE route. This first test establishes Cromwell → FreeLoader. Reproduce through an Xromwell XBE on a private dashboard fixture before physical UnleashX testing.

| Marker | What it establishes |
| --- | --- |
| XWN10 | FreeLoader reached its Xbox platform initialization marker |
| XWN20 | Its memory manager initialized |
| XWN30 | Boot-device initialization returned success; the boot path is printed |
| XWN40 | The diagnostic printed the firmware memory descriptors and halted before Windows |

Allow up to three minutes for each initial attempt, including any Cromwell menu selection. Capture the last marker, framebuffer, emulator logs and register state if stalled. **Pass:** three cold boots with XWN40, identical input hashes, an explicit 64 MiB configuration, and a reviewed memory map reserving the framebuffer and excluding invalid/free overlaps. XWN40 alone does not certify the map or disk contents. This probe reports discovery; it does not yet verify file-data reads or the final NT memory map.

## What follows the diagnostic

Build the normal loader with `./Invoke-Build.ps1 -Stage loader` only after reviewing the diagnostic results. Package `freeldr.sys`, `rosload.exe` and an explicit `BootType=Windows2000` configuration with an appropriately prepared Windows fixture. The selected ISO is `EN_WIN2000_PRO_SP4.ISO`; no additional ISO is needed now.

Before an Xbox Windows-kernel test, resolve the HAL import/forwarder and structure compatibility issues in the audit, verify the boot-video dependency, and arrange a trace at **relocated kernel base + entry RVA `0xD1F0`**. The PE preferred base is not necessarily the runtime load address. A pre-jump loader message is insufficient evidence.

Preparing an installed SYSTEM hive, driver registrations and a writable Windows system volume remains a separate build/test stage. A conventional Windows 2000 PC VM could later prepare or control-test that fixture if desired; its results would not establish Xbox hardware support. Physical disk layout and hardware revision remain unresolved and do not block this first emulator diagnostic.

## Validation already performed

Seven synthetic binary-validator cases passed, including malformed checksum, oversized file, invalid entry, wrong CPU, low-memory overflow and misplaced header rejection. Synthetic and real ISO readback checks passed. Both real FreeLoader variants pass the packaging validator. Source patches passed applicability and whitespace checks; Bash and PowerShell syntax checks passed. Three real diagnostic cold boots passed as recorded in the [results](../native-windows-build/test-results.json). No Windows code was executed.
