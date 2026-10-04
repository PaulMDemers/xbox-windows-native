#requires -Version 7.4
param(
 [Parameter(Mandatory)][ValidatePattern('^nt5-fatx-boot-rename-[0-9]+$')][string]$RunId,
 [Parameter(Mandatory)][ValidateSet('before','after','final','complete')][string]$Variant
)
$ErrorActionPreference='Stop'
$manifest=Get-Content -Raw (Join-Path $PSScriptRoot "rename-$Variant-fixture-001.json") | ConvertFrom-Json
$disk=Join-Path $PSScriptRoot "artifacts/windows2000-fatx-rename-$Variant-001.qcow2"
$iso=Join-Path $PSScriptRoot ../native-windows-bootvid-framebuffer/artifacts/bootvid-ram-001.iso
if ((Get-FileHash $disk).Hash -ne $manifest.sha256) { throw 'Rename fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '605DD66EFF552538B2940159DDF1E41EC4EFCE9766739E5BD8CA6A0AC833A8EF') { throw 'Boot ISO changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -AllowFramebufferFallback -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Inspect owned emulator run logs.' }
