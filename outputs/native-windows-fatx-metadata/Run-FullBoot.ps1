#requires -Version 7.4
param([ValidatePattern('^nt5-fatx-boot-metadata-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
if (!$RunId) { throw 'Supply a new nt5-fatx-boot-metadata-NNN run id.' }
$disk=Join-Path $PSScriptRoot artifacts/windows2000-fatx-metadata-001.qcow2
$iso=Join-Path $PSScriptRoot ../native-windows-bootvid-framebuffer/artifacts/bootvid-ram-001.iso
if ((Get-FileHash $disk).Hash -ne '66ED7D44FA987CEF27A2E59DF06722D43E1A4C64C30ADEED62CA0D718B565B09') { throw 'FATX fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '605DD66EFF552538B2940159DDF1E41EC4EFCE9766739E5BD8CA6A0AC833A8EF') { throw 'FATX boot ISO changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -AllowFramebufferFallback -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Emulator harness failed; inspect run logs.' }
