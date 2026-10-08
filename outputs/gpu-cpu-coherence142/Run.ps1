#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$f=Get-Content (Join-Path $PSScriptRoot 'fixture-control001.json') -Raw | ConvertFrom-Json
$seed=Join-Path $ws 'work/gpu-cpu-coherence142-control001-seed.qcow2'
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne $f.seed_sha256){throw 'Seed changed'}
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected experiment environment'}
if(Test-Path (Join-Path $PSScriptRoot 'control001/runner-start.json')){throw 'No duplicate launch'}
@{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;physical_access=$false;debugger=$false;performance_qualified=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'control001/runner-start.json')
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & (Join-Path $PSScriptRoot '../video-surface-history/Invoke-Exclusive.ps1') -RunId gpu-coherence142-control001 -InstanceTask windows-native-gpu142 `
  -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
  -Iso (Join-Path $PSScriptRoot '../native-windows-extended-storage/artifacts/f-boot-length-004.iso') `
  -HddSource $seed -EepromSource (Join-Path $ws 'work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin') `
  -EmulatorPath (Join-Path $PSScriptRoot '../native-windows-physical-f/artifacts/xemu-resource-model.exe') `
  -EmulatorSha256 969a99a83a308ba547ce3918015d676efee79912d97253d336bf8a35b5bc047d `
  -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -CompactTrace -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 360
}
