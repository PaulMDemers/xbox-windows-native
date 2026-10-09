#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected experiment environment'}
$out=Join-Path $PSScriptRoot cancel005
if(Test-Path (Join-Path $out runner-start.json)){throw 'Never relaunch'}
$pins=Get-Content (Join-Path $PSScriptRoot frozen-cancel005.json) -Raw | ConvertFrom-Json
foreach($item in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $item.Name)).Hash.ToLowerInvariant() -ne $item.Value){throw ('Frozen input changed: '+$item.Name)}}
$f=Get-Content (Join-Path $PSScriptRoot fixture-cancel005.json) -Raw | ConvertFrom-Json
$seed=$f.fixture_path_windows
if((Get-PSDrive C).Free - (Get-Item -LiteralPath $seed).Length - 512MB -lt 20GB){throw 'Projected copy/headroom would violate20GiB guard'}
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne $f.seed_sha256){throw 'Seed changed'}
$exe=Join-Path $PSScriptRoot ../xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe
$digest='685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Emulator changed'}
if(Test-Path (Join-Path $ws work/runs/nt5-wizard201-cancel005)){throw 'Run exists'}
@{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;emulator_sha256=$digest;physical_access=$false;debugger=$false;ordinary_qualified=$false;guest_restart_guard_enabled=$true;normal_restart_requested_before_launch=$false} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & (Join-Path $PSScriptRoot ../video-surface-history/Invoke-Exclusive.ps1) -RunId nt5-wizard201-cancel005 -InstanceTask windows-native-wizard201 `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
 -Iso (Join-Path $PSScriptRoot ../native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
 -HddSource $seed -EepromSource (Join-Path $ws work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin) `
 -EmulatorPath $exe -EmulatorSha256 $digest -CaptureWidth 640 -CaptureHeight 480 -CapturePitch 2560 `
 -FtpPort 4596 -MonitorPort 4594 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 300
}
