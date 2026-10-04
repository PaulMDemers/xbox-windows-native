#requires -Version 7.4
param(
 [Parameter(Mandatory)][ValidatePattern('^nt5-fatx-boot-power-[0-9]+$')][string]$RunId,
 [ValidateSet('no-audio','no-audio-network')][string]$Mode='no-audio-network'
)
$ErrorActionPreference='Stop'
$disk=Join-Path $PSScriptRoot "artifacts/windows2000-fatx-$Mode-001.qcow2"
$manifest=Get-Content (Join-Path $PSScriptRoot "$Mode-disk-001.json") -Raw | ConvertFrom-Json
$iso=Join-Path $PSScriptRoot ../native-windows-fatx-boot/artifacts/fatx-boot-001.iso
if ((Get-FileHash $disk).Hash -ne $manifest.sha256) { throw 'Isolation fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '8AF80464D11FE100C1042D223A914D0AB0314E9C85D8D78E338DD1E7D70A04ED') { throw 'FATX boot ISO changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Inspect emulator harness logs.' }
