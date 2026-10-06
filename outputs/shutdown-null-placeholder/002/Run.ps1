#requires -Version 7.4
param([ValidateSet('001','002','003')][string]$Case='001')
$ErrorActionPreference='Stop'
if (!$Case) { throw 'Case required' }
$ws=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$fixture=Get-Content (Join-Path $PSScriptRoot ('fixture-'+$Case+'.json')) -Raw | ConvertFrom-Json
$seed=Join-Path $ws ('work/shutdown-null-placeholder-'+$Case+'-seed.qcow2')
if ((Get-FileHash $seed).Hash -ne $fixture.seed_sha256) { throw 'Seed changed' }
if (Test-Path (Join-Path $ws ('work/runs/nt5-shutdown-null-placeholder-'+$Case))) { throw 'Attempt already exists' }
if ($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL) { throw 'Unexpected experiment environment' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId ('nt5-shutdown-null-placeholder-'+$Case) `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
 -Iso (Join-Path $PSScriptRoot ../native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
 -HddSource $seed -EepromSource (Join-Path $ws work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin) `
 -EmulatorPath (Join-Path $PSScriptRoot ../native-windows-physical-f/artifacts/xemu-resource-model.exe) `
 -EmulatorSha256 969a99a83a308ba547ce3918015d676efee79912d97253d336bf8a35b5bc047d `
 -CaptureWidth 1024 -CaptureHeight 576 -CapturePitch 4096 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 `
 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -StopOnBugcheck -Seconds 600
