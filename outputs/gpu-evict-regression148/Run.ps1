#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('control001','candidate001')][string]$Case)
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$f=Get-Content (Join-Path $PSScriptRoot ('fixture-'+$Case+'.json')) -Raw | ConvertFrom-Json
$build=Get-Content (Join-Path $PSScriptRoot '../xemu-cpu-surface-evict/build003/build.json') -Raw | ConvertFrom-Json
$role=$Case.Replace('001','')
$exe=Join-Path $PSScriptRoot ('../xemu-cpu-surface-evict/build003/artifacts/xemu-'+$role+'.exe')
$digest=($build.builds | Where-Object {$_.case -eq $role}).sha256
$seed=Join-Path $ws ('work/gpu-regression148-regression148-'+$Case+'-seed.qcow2')
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne $f.seed_sha256){throw 'Seed changed'}
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Executable changed'}
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected experiment environment'}
$record=Join-Path $PSScriptRoot ($Case+'/runner-start.json')
if(Test-Path $record){throw 'No duplicate launch'}
@{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;case=$Case;emulator_sha256=$digest;physical_access=$false;debugger=$false;performance_qualified=$false} | ConvertTo-Json | Set-Content $record
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & (Join-Path $PSScriptRoot '../video-surface-history/Invoke-Exclusive.ps1') -RunId ('gpu-regression148-'+$Case) -InstanceTask ('windows-native-evict-'+$role) `
  -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
  -Iso (Join-Path $PSScriptRoot '../native-windows-extended-storage/artifacts/f-boot-length-004.iso') `
  -HddSource $seed -EepromSource (Join-Path $ws 'work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin') `
  -EmulatorPath $exe -EmulatorSha256 $digest `
  -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -CompactTrace -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 360
}
