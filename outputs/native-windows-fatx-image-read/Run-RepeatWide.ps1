#requires -Version 7.4
param([ValidatePattern('^nt5-fatx-boot-image-read-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
if (!$RunId) { throw 'Supply a new nt5-fatx-boot-image-read-NNN run id.' }
$disk=Join-Path $PSScriptRoot ../../work/runs/nt5-fatx-boot-image-read-001/hdd.qcow2
$iso=Join-Path $PSScriptRoot ../native-windows-fatx-boot/artifacts/fatx-boot-001.iso
if ((Get-FileHash $disk).Hash -ne '949127FD3CA4A7D4AD62671394B8D4CC14A678D495717E5148F0B31C4BC55D45') { throw 'FATX fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '8AF80464D11FE100C1042D223A914D0AB0314E9C85D8D78E338DD1E7D70A04ED') { throw 'FATX boot ISO changed.' }
$eeprom=Join-Path $PSScriptRoot ../../work/paging-v3-widescreen-eeprom.bin
if ((Get-FileHash $eeprom).Hash -ne '8B4A8A97E21797E2F94EA8C953B1D3432AC91D1D5CC8783C031E3823BAFA924A') { throw 'Widescreen EEPROM fixture changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -EepromSource $eeprom -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Emulator harness failed; inspect run logs.' }
