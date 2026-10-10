#requires -Version 7.4
param([ValidateSet('trace001')][string]$Case)
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected experiment environment'}
$out=Join-Path $PSScriptRoot $Case
if(Test-Path (Join-Path $out runner-start.json)){throw 'Never relaunch'}
$pins=Get-Content (Join-Path $PSScriptRoot emulator-frozen.json) -Raw | ConvertFrom-Json
foreach($item in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $item.Name)).Hash.ToLowerInvariant() -ne $item.Value){throw ('Frozen input changed: '+$item.Name)}}
$f=Get-Content (Join-Path $PSScriptRoot ("fixture-$Case.json")) -Raw | ConvertFrom-Json
$seed=$f.fixture_path_windows
if((Get-PSDrive E).Free - (Get-Item -LiteralPath $seed).Length - 512MB -lt 20GB){throw 'Projected copy/headroom would violate20GiB guard'}
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne $f.seed_sha256){throw 'Seed changed'}
$exe=Join-Path $PSScriptRoot ../xemu-backend-reason228/artifacts/build002/xemu-preserve227.exe
$digest=(Get-Content (Join-Path $PSScriptRoot ../xemu-backend-reason228/build002.json) -Raw | ConvertFrom-Json).executable_sha256
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Emulator changed'}
if(Test-Path (Join-Path "E:/Codex-private-artifacts/xbox-windows-feasibility/dashboard230-runs" ("nt5-dashboard230-$Case"))){throw 'Run exists'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 @{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;emulator_sha256=$digest;physical_access=$false;debugger=$true;ordinary_qualified=$false;guest_restart_guard_enabled=$true;normal_restart_requested_before_launch=$false} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
 & (Join-Path $PSScriptRoot Invoke-230.ps1) -RunId ("nt5-dashboard230-$Case") -InstanceTask windows-native-dashboard230 `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
 -Iso (Join-Path $PSScriptRoot ../native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
 -HddSource $seed -EepromSource (Join-Path $ws work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin) `
 -EmulatorPath $exe -EmulatorSha256 $digest -CaptureWidth 640 -CaptureHeight 480 -CapturePitch 2560 `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 480
}
}
