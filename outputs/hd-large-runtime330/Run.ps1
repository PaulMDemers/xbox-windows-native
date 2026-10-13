#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('emu001')][string]$Case)
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$out=Join-Path $PSScriptRoot $Case
$env:PYTHONUTF8='1'
$env:PYTHONPATH=Join-Path $ws work/python-packages
& C:/Python314/python.exe -B -c 'from PIL import Image; import PIL._imaging'
if($LASTEXITCODE){throw 'Image dependency unavailable before launch'}
if(Test-Path (Join-Path $out runner-start.json)){throw 'Never repeat accepted attempt'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected diagnostic environment'}
$f=Get-Content (Join-Path $out fixture.json) -Raw | ConvertFrom-Json
$build=Get-Content (Join-Path $PSScriptRoot '../pramdac-timing322/build003.json') -Raw | ConvertFrom-Json
if(-not $build.passed -or -not $build.borrowed_sources_restored){throw 'Unqualified emulator build'}
$exe='E:/xwn329/retained-builds001/xemu-hd322.exe'
$digest='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Emulator pin mismatch'}
if((Get-PSDrive C).Free - 64MB -lt 20GB){throw 'Projected C 20GiB guard'}
if((Get-PSDrive E).Free - (Get-Item $f.fixture_path_windows).Length - 512MB -lt 20GB){throw 'Projected E reserve'}
if((Get-FileHash $f.fixture_path_windows).Hash.ToLowerInvariant() -ne $f.fixture_sha256){throw 'Fixture changed'}
foreach($p in ((Get-Content (Join-Path $PSScriptRoot host-frozen.json) -Raw | ConvertFrom-Json).PSObject.Properties)){if((Get-FileHash -LiteralPath $p.Name).Hash.ToLowerInvariant() -ne $p.Value){throw 'Host dependency changed'}}
$pins=Get-Content (Join-Path $PSScriptRoot emulator-frozen.json) -Raw | ConvertFrom-Json
foreach($item in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $item.Name)).Hash.ToLowerInvariant() -ne $item.Value){throw ('Frozen input changed: '+$item.Name)}}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  @{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;emulator_sha256=$digest;physical_access=$false;debugger=$false;ordinary_qualified=$false} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
  & (Join-Path $PSScriptRoot Invoke.ps1) -RunId "nt5-hd330-$Case" -InstanceTask "windows-native-hd330-$Case" `
   -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
   -Iso (Join-Path $ws outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
   -HddSource $f.fixture_path_windows -EepromSource E:/xwn289/fixture001/hd.bin `
   -EmulatorPath $exe -EmulatorSha256 $digest -FtpPort 5106 -MonitorPort 5104 -GdbPort 5105 `
   -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -CaptureAudio -CaptureWidth 1920 -CaptureHeight 1080 -CapturePitch 7680 -Seconds 1200
 }
}
