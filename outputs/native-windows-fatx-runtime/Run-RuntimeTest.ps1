#requires -Version 7.4
param([ValidatePattern('^nt5-fatx-runtime-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
if (!$RunId) { throw 'Supply a new nt5-fatx-runtime-NNN run id.' }
$disk=Join-Path $PSScriptRoot artifacts/windows2000-fatx-runtime-001.qcow2
if ((Get-FileHash $disk).Hash -ne '1EF5A449E365E84BF757A5F9CB96AF912646FDF03159B20A96677FE83A58C091') { throw 'Runtime fixture changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
 -Iso (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/artifacts/kernel-autorun-006.iso) `
 -HddSource $disk -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 `
 -LaunchXromwell -UsbMouse -Autorun -RetainDisk -Seconds 150
if($LASTEXITCODE){throw 'Emulator run failed; inspect private run logs.'}
