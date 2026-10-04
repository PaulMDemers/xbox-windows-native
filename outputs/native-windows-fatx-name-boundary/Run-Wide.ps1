#requires -Version 7.4
param([Parameter(Mandatory)][ValidatePattern('^nt5-fatx-boot-wide-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
$disk=Join-Path $PSScriptRoot ../native-windows-fatx-name-boundary/artifacts/windows2000-fatx-name-boundary-001.qcow2
$iso=Join-Path $PSScriptRoot ../native-windows-bootvid-framebuffer/artifacts/bootvid-ram-001.iso
$eeprom=Join-Path $PSScriptRoot ../../work/paging-v3-widescreen-eeprom.bin
if ((Get-FileHash $disk).Hash -ne 'A4005A8D560312FCD0C6EC9F4EB176C520C69B7EF1F62F627C89AA6900E8F864') { throw 'FATX fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '605DD66EFF552538B2940159DDF1E41EC4EFCE9766739E5BD8CA6A0AC833A8EF') { throw 'FATX boot ISO changed.' }
if ((Get-FileHash $eeprom).Hash -ne '8B4A8A97E21797E2F94EA8C953B1D3432AC91D1D5CC8783C031E3823BAFA924A') { throw 'Wide EEPROM fixture changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -EepromSource $eeprom -CaptureWidth 1024 -CaptureHeight 576 -CapturePitch 4096 `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -AllowFramebufferFallback -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Inspect emulator harness logs.' }
