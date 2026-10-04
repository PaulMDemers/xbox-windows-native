#requires -Version 7.4
param([ValidatePattern('^nt5-fatx-boot-hal-paging-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
if (!$RunId) { throw 'Supply a new nt5-fatx-boot-hal-paging-NNN run id.' }
$disk=Join-Path $PSScriptRoot ../native-windows-fatx-flush/artifacts/windows2000-fatx-full-flush-001.qcow2
$iso=Join-Path $PSScriptRoot artifacts/hal-paging-002.iso
if ((Get-FileHash $disk).Hash -ne '0C94140B312F4B74E5E0C2CE3109AC6E8E83520D5A6898CA652945FE160C2A57') { throw 'FATX fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '2AE5B45F921336F7CAAC11CF0AEFBC6C96D2F7D9A88022D64BF2A1011D3DE2AB') { throw 'FATX boot ISO changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Emulator harness failed; inspect run logs.' }
