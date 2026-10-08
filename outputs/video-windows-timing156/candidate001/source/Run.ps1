#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('control001','candidate001')][string]$Case)
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected experiment environment'}
$ready=Get-Content (Join-Path $PSScriptRoot fixtures-ready.json) -Raw | ConvertFrom-Json
if(!$ready.passed){throw 'Both fixtures must be prepared before timing'}
$preflight=Get-Content (Join-Path $PSScriptRoot ($Case+'/preflight.json')) -Raw | ConvertFrom-Json
if(!$preflight.passed){throw 'Pinned preflight missing'}
if(Test-Path (Join-Path $PSScriptRoot ($Case+'/runner-start.json'))){throw 'Never relaunch'}
$pins=Get-Content (Join-Path $PSScriptRoot frozen-inputs.json) -Raw | ConvertFrom-Json
foreach($item in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $item.Name)).Hash.ToLowerInvariant() -ne $item.Value){throw ('Frozen input changed: '+$item.Name)}}
$f=Get-Content (Join-Path $PSScriptRoot ('fixture-'+$Case+'.json')) -Raw | ConvertFrom-Json
$seed=Join-Path $ws ('work/video-windows-timing156-'+$Case+'-seed.qcow2')
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne $f.seed_sha256){throw 'Seed changed'}
$allocation=Get-Content (Join-Path $PSScriptRoot ($Case+'/before/allocation.json')) -Raw | ConvertFrom-Json
if(!$allocation.allocation_consistent -or $allocation.errors.Count -or $allocation.orphan_cluster_count){throw 'Invalid pre-run allocation'}
$build=Get-Content (Join-Path $PSScriptRoot '../xemu-cpu-surface-evict/build003/build.json') -Raw | ConvertFrom-Json
$role=$Case.Replace('001','');$digest=($build.builds | Where-Object {$_.case -eq $role}).sha256
$exe=Join-Path $PSScriptRoot ('../xemu-cpu-surface-evict/build003/artifacts/xemu-'+$role+'.exe')
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Emulator changed'}
if(Test-Path (Join-Path $ws ('work/runs/nt5-vtime156-'+$Case))){throw 'Run already exists'}
if($Case -eq 'candidate001' -and !(Test-Path (Join-Path $ws work/runs/nt5-vtime156-control001/cleanup.json))){throw 'Control must be closed first'}
@{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;case=$Case;emulator_sha256=$digest;physical_access=$false;debugger=$false;performance_qualified=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot ($Case+'/runner-start.json'))
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 $path=Join-Path $PSScriptRoot ($Case+'/performance-lease.json')
 if(Test-Path $path){throw 'Lease record exists'}
 $lease=[ordered]@{build_held=$true;exclusive_xemu_requested=$true;owner_pid=$PID;started_utc=[DateTime]::UtcNow.ToString('o');finished=$false}
 $lease | ConvertTo-Json | Set-Content $path
 try {
  & (Join-Path $PSScriptRoot '../video-surface-history/Invoke-Exclusive.ps1') -RunId ('nt5-vtime156-'+$Case) -InstanceTask ('windows-native-evict-'+$role) `
  -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
  -Iso (Join-Path $PSScriptRoot '../native-windows-extended-storage/artifacts/f-boot-length-004.iso') `
  -HddSource $seed -EepromSource (Join-Path $ws 'work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin') `
  -EmulatorPath $exe -EmulatorSha256 $digest -CaptureWidth 1024 -CaptureHeight 576 -CapturePitch 4096 `
  -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 1200
  $lease.finished=$true
 } finally {
  $lease.finished_utc=[DateTime]::UtcNow.ToString('o');$lease | ConvertTo-Json | Set-Content $path
 }
}
