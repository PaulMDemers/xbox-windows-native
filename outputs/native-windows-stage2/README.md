# Native Xbox Windows: second-stage and dashboard checkpoint

3 October 2026. **The 64 MiB emulator now completes UnleashX → Xromwell XBE → FreeLoader → rosload.** Two independent dashboard launches reached the same verified diagnostic stop as the direct Cromwell ROM boot. This establishes the dashboard/XBE handoff in xemu; it does not establish the physical softmod exploit or a Windows kernel boot.

![Second-stage diagnostic completion](evidence/unleashx-ftp-003/frame-045.png)

## Implemented and tested

The new opt-in `XBOX_NATIVE_IO_PREFLIGHT` mode verifies a deterministic 131,075-byte CD file, EOF and a 31-byte seek/read starting at byte 2041, across a CD sector boundary. It then uses the existing PE loader to load, relocate, bind imports and enter `rosload.exe`. The second stage repeats the file verification through imported FreeLoader services and checks a token read by the existing INI parser. It halts before any Windows loader path.

| Test | Observed result |
| --- | --- |
| Direct Cromwell ROM, correct disc | XWN50, XWN60, XWN70 and XWN80; halted in rosload |
| One corrupted byte at offset 65537 | First-stage verification failed in the block starting at 65536; no second-stage entry |
| Wrong INI token | rosload entered, then rejected the configuration; no final success marker |
| UnleashX/Xromwell launch 1 | XWN80; identical final framebuffer to the direct ROM route |
| UnleashX/Xromwell launch 2 | XWN80 again; identical final framebuffer |

The two negative images have the same loader binaries as the positive image. Their data/configuration differ intentionally. This checks failure behavior as well as the successful path. ISO contents were also extracted and compared byte-for-byte before boot.

UnleashX came from the supplied `UnleashX.zip`; its included readme identifies the package as unofficial 0.39.0528 build 584. Its XBE was staged unchanged. A private configuration contains a single diagnostic menu entry, and the existing dashboard disk was converted to a private FATX staging image. Every injected file was read back and hash-verified. The original disk and ZIP were not modified.

![UnleashX before launching Xromwell](evidence/unleashx-ftp-003/frame-030.png)

The generic emulated USB keyboard did not activate the menu. The successful runs instead used UnleashX's documented `SITE EXEC` command to launch `E:\Apps\XWN\default.xbe`. The guest returned `200 EXEC command succeeded.` before Xromwell took over. This tests the dashboard's XBE launcher, not a gamepad/menu-navigation path. [UnleashX changes, FTP launch command](https://github.com/Rocky5/Xbox-Softmodding-Tool/blob/master/Documents/UnleashX%20Changes.txt).

The FTP control connection was forwarded only from `127.0.0.1:4575` into QEMU's restricted user network. No data transfers were needed. The guest network was restricted from external connections. A private monitor used port 4574. Each run used a private EEPROM, snapshot disk and managed process/scratch lease; the staging disk copy and snapshot overlay were removed when it ended.

Two harness issues were corrected during investigation: xemu needed the configured network-backend identity and an explicit link-up command for the restricted connection, and simultaneous monitor clients could interfere with a capture. The monitor helper now serializes complete pause/capture/resume operations with a task-local lock. Dashboard captures read the NV2A framebuffer address rather than assuming Cromwell's fixed address. The early dashboard/control failures remain in the logs and are not counted as passes.

## Actual HAL and boot-video findings

Both debug and release `halxbox.dll` and `xboxbvid.dll` built. The release build has `DBG=0` and HAL build type 2 (uniprocessor, free). The supplied Windows kernel exposes `NtBuildNumber=0xF0000893`. Merely selecting Release leaves the following concrete link failures:

| Direction | Missing names/targets |
| --- | --- |
| Windows kernel → Xbox HAL | `KdPortGetByte`, `KdPortInitialize`, `KdPortPollByte`, `KdPortPutByte`, `KdPortRestore`, `KdPortSave` |
| Xbox HAL → Windows kernel | `IoAssignDriveLetters`, `IoReadPartitionTable`, `IoSetPartitionInformation`, `IoWritePartitionTable`, `KeTryToAcquireSpinLockAtDpcLevel`, `KiEoiHelper`, `RtlClearBit` |
| Xbox HAL forwarded exports → Windows kernel | `ExiAcquireFastMutex`, `ExiReleaseFastMutex`, `ExiTryToAcquireFastMutex` |

The release HAL imports 86 kernel names, seven of which are absent. Its three fast-mutex forwarders are unresolved. In contrast, all ten Windows kernel imports from `bootvid.dll` exist in `xboxbvid.dll`, and all nine release boot-video kernel imports exist in the supplied kernel. That is a successful **name-level** boot-video audit; calling conventions, structures and display behavior remain untested.

The compiled [layout probe](hal-layout-probe.json) uses the exact release HAL compiler flags, rather than guessed header settings:

| Contract | Supplied Windows 2000 kernel | Current ReactOS build |
| --- | --- | --- |
| Public HAL dispatch version | 2 | 3 |
| Private HAL dispatch version | 1 | 2 |
| Target NTDDI | Windows 2000 media | `0x05020000` |

The source registers debugger callbacks through private-table fields at offsets `0x34` through `0x4C`; those fields belong to the newer contract. `HalInitializeProcessor` calls that registration even before normal HAL initialization. This needs an explicit Windows 2000 path; changing exports alone cannot resolve it. The probe also records PCR/PRCB field offsets and trap-frame/fast-mutex sizes for subsequent comparison. It does **not** establish that Windows 2000 uses all those layouts.

The [release binary audit](hal-free-binary-audit.json) and [debug audit](hal-binary-audit.json) retain complete import/export tables and hashes. Running `audit_hal_binaries.py --flavor free --require-compatible` intentionally fails for the current candidate. No Windows kernel was loaded with it, and no no-op compatibility stubs were introduced.

## Next implementation work

1. Create a separate Windows 2000 HAL target with the correct public/private dispatch definitions and guarded debugger registration. Validate PCR/PRCB, trap frame and fast-mutex layouts against the supplied kernel before retaining direct structure accesses.
2. Implement the HAL-owned fast mutex and legacy debugger-port interfaces. Replace the ReactOS-specific `KiEoiHelper` dependency with a verified NT 5.0 interrupt-exit path; this is the most consequential execution-contract gap.
3. Move partition/drive-letter responsibilities into an NT 5.0-compatible implementation. The current HAL delegates to kernel exports that Windows 2000 does not provide. Preserve the Xbox partition rules and PCI exclusions while doing this.
4. Prepare an installed Windows 2000 system volume and SYSTEM hive with a deliberate boot-storage driver configuration. Confirm file loading and the actual NT loader block before a traced kernel entry attempt.

The supplied `EN_WIN2000_PRO_SP4.ISO` remains sufficient. No additional ISO is needed at this checkpoint. Hardware revision and a recovery/test-disk arrangement remain needed before physical deployment.

## Reproduction and artifacts

The source base remains ReactOS `afc0127e8f937ab68503d715d948844973756aa1`. Apply [0005-native-io-cumulative.patch](../native-windows-prebuild/patches/0005-native-io-cumulative.patch) to that base. It **replaces** patch 0001 and includes the original diagnostic and Windows 2000 dispatch change; do not apply both. The updated source-preparation script selects it automatically for fresh clones.

Build with `Invoke-Build.ps1 -Stage io`, `-Stage hal-audit` and `-Stage hal-free-audit`. The normal loader was rebuilt successfully with the new probe disabled; that variant has not been runtime-tested. The first diagnostic mode remains available. Original stage-one binaries remain preserved in the earlier build folder.

[Positive test disc](artifacts/io-good.iso), [FreeLoader](artifacts/freeldr.sys), [rosload](artifacts/rosload.exe), [result manifest](test-results.json), [file hashes](manifest.json). The two deliberately failing test ISOs are alongside the positive one. HAL binaries under `artifacts/hal-audit` and `artifacts/hal-free-audit` are audit artifacts, not Windows-ready replacements.

`stage_unleashx.py` expects a fresh private RAW conversion at `/home/paul/xbox-windows-native/fixtures/dashboard-inspection.raw`; it refuses an already-staged fixture. `enable-fixture-ftp.py` in the build kit records the restricted-FTP configuration variant. The retained reusable fixture is `work/unleashx-ftp-fixture.qcow2`; each emulator run copies it before using snapshot mode. To repeat a successful launch, use a fresh run ID:

```powershell
./outputs/native-windows-prebuild/Invoke-Diagnostic.ps1 `
  -RunId unleashx-ftp-005 `
  -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
  -Iso ./outputs/native-windows-stage2/artifacts/io-good.iso `
  -HddSource ./work/unleashx-ftp-fixture.qcow2 `
  -FtpPort 4575 -LaunchXromwell -Seconds 60
```

This uses the existing Complex firmware to start the dashboard. Physical UnleashX softmod boot remains a separate test; neither firmware flashing nor writes to the real console were performed.
