#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('candidate001')][string]$Case)
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected experiment environment'}
$ready=Get-Content (Join-Path $PSScriptRoot emulator-ready.json) -Raw | ConvertFrom-Json
if(!$ready.passed){throw 'Both prepared/preflighted fixtures required'}
if(Test-Path (Join-Path $PSScriptRoot ($Case+'/runner-start.json'))){throw 'Never relaunch'}
$pins=Get-Content (Join-Path $PSScriptRoot helper-frozen-inputs.json) -Raw | ConvertFrom-Json
foreach($item in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $item.Name)).Hash.ToLowerInvariant() -ne $item.Value){throw ('Frozen input changed: '+$item.Name)}}
$f=Get-Content (Join-Path $PSScriptRoot ('fixture-'+$Case+'.json')) -Raw | ConvertFrom-Json
$seed=Join-Path $ws ('work/video-hardware-trial164-'+$Case+'-seed.qcow2')
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne $f.seed_sha256){throw 'Seed changed'}
$exe=Join-Path $PSScriptRoot '../xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe'
$digest='685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Emulator changed'}
if(Test-Path (Join-Path $ws ('work/runs/nt5-vphys164-'+$Case))){throw 'Run exists'}
if($Case -eq 'candidate001'){
 $control=Get-Content (Join-Path $PSScriptRoot '../video-physical-rehearsal162/control001/audit.json') -Raw | ConvertFrom-Json
 if(!$control.workload_passed -or !$control.integrity_passed){throw 'Control diagnostic prerequisites failed'}
}
@{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;case=$Case;emulator_sha256=$digest;physical_access=$false;debugger=$false;performance_qualified=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot ($Case+'/runner-start.json'))
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & (Join-Path $PSScriptRoot '../video-surface-history/Invoke-Exclusive.ps1') -RunId ('nt5-vphys164-'+$Case) -InstanceTask windows-native-physical-hardware-trial164 `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
 -Iso (Join-Path $PSScriptRoot '../native-windows-extended-storage/artifacts/f-boot-length-004.iso') `
 -HddSource $seed -EepromSource (Join-Path $ws 'work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin') `
 -EmulatorPath $exe -EmulatorSha256 $digest -CaptureWidth 640 -CaptureHeight 480 -CapturePitch 2560 `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 480
}
