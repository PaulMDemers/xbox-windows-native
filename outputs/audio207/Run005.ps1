#requires -Version 7.4
param([ValidateSet('candidate004')][string]$Case)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$original='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility'
$out=Join-Path $PSScriptRoot $Case
$env:PYTHONPATH='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages'
$deps=Get-Content (Join-Path $PSScriptRoot host-dependencies002.json) -Raw | ConvertFrom-Json
foreach($p in $deps.PSObject.Properties){if((Get-FileHash $p.Name).Hash.ToLowerInvariant() -ne $p.Value){throw 'Host Pillow dependency changed'}}
& python -c "from PIL import Image; import PIL._imaging"
if($LASTEXITCODE){throw 'Host image dependency preflight failed before guest creation'}
$f=Get-Content (Join-Path $out fixture.json) -Raw | ConvertFrom-Json
if(Test-Path (Join-Path $out runner-start.json)){throw 'Never relaunch closed or started case'}
if((Get-PSDrive C).Free - 128MB -lt 20GB){throw 'Projected C reserve guard'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected emulator experiment environment'}
if((Get-FileHash $f.fixture_path_windows).Hash.ToLowerInvariant() -ne $f.fixture_sha256){throw 'Fixture changed'}
$exe=Join-Path $original 'outputs/xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe'
$digest='685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Emulator changed'}
$pins=Get-Content (Join-Path $PSScriptRoot frozen005.json) -Raw | ConvertFrom-Json
foreach($p in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $repo $p.Name)).Hash.ToLowerInvariant() -ne $p.Value){throw ('Frozen source changed: '+$p.Name)}}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
  & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
    @{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;emulator_sha256=$digest;physical_access=$false;debugger=$false;ordinary_qualified=$false} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
    & (Join-Path $PSScriptRoot 'Invoke-Audio.ps1') -RunId ('nt5-audio207-'+$Case) -InstanceTask windows-native-audio207 `
        -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
        -Iso (Join-Path $original 'outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso') `
        -HddSource $f.fixture_path_windows -EepromSource (Join-Path $original 'work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin') `
        -EmulatorPath $exe -EmulatorSha256 $digest -FtpPort 4696 -MonitorPort 4694 -GdbPort 4695 `
        -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -CaptureAudio -Seconds 360
  }
}
