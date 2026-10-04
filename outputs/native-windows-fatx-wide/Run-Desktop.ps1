#requires -Version 7.4
param([Parameter(Mandatory)][ValidatePattern('^nt5-fatx-boot-wide-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
$disk=Join-Path $PSScriptRoot ../native-windows-fatx-flush/artifacts/windows2000-fatx-full-flush-001.qcow2
$iso=Join-Path $PSScriptRoot ../native-windows-fatx-boot/artifacts/fatx-boot-001.iso
$eeprom=Join-Path $PSScriptRoot ../../work/paging-v3-widescreen-eeprom.bin
if ((Get-FileHash $disk).Hash -ne '0C94140B312F4B74E5E0C2CE3109AC6E8E83520D5A6898CA652945FE160C2A57') { throw 'FATX fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '8AF80464D11FE100C1042D223A914D0AB0314E9C85D8D78E338DD1E7D70A04ED') { throw 'FATX boot ISO changed.' }
if ((Get-FileHash $eeprom).Hash -ne '8B4A8A97E21797E2F94EA8C953B1D3432AC91D1D5CC8783C031E3823BAFA924A') { throw 'Wide EEPROM fixture changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -EepromSource $eeprom -CaptureWidth 1024 -CaptureHeight 576 -CapturePitch 4096 `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -StopOnBugcheck -StopOnCaptureComplete -Seconds 420
if ($LASTEXITCODE) { throw 'Inspect emulator harness logs.' }
