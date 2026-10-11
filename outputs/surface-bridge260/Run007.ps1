#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$out=Join-Path $PSScriptRoot emu007
$env:PYTHONUTF8='1'
$env:PYTHONPATH=Join-Path $ws work/python-packages
& C:/Python314/python.exe -B -c 'from PIL import Image; import PIL._imaging'
if($LASTEXITCODE){throw 'Image dependency unavailable before launch'}
if(Test-Path (Join-Path $out runner-start.json)){throw 'Never repeat accepted attempt'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected diagnostic environment'}
$f=Get-Content (Join-Path $out fixture.json) -Raw | ConvertFrom-Json
$exe='E:/Codex-archive/xbox-windows-native/bridge260-build001/xemu-bridge260.exe'
$digest='6bf95a6330a07261c206c00b051fc0b0ca17be2f1a3483374cff362712f33d14'
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $digest){throw 'Emulator pin mismatch'}
if((Get-PSDrive C).Free - (Get-Item $exe).Length - 128MB -lt 20GB){throw 'Projected C 20GiB guard'}
if((Get-PSDrive E).Free - (Get-Item $f.fixture_path_windows).Length - 512MB -lt 20GB){throw 'Projected E reserve'}
if((Get-FileHash $f.fixture_path_windows).Hash.ToLowerInvariant() -ne $f.fixture_sha256){throw 'Fixture changed'}
$pins=Get-Content (Join-Path $PSScriptRoot emulator-frozen007.json) -Raw | ConvertFrom-Json
foreach($item in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $item.Name)).Hash.ToLowerInvariant() -ne $item.Value){throw ('Frozen input changed: '+$item.Name)}}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  @{utc=[DateTime]::UtcNow.ToString('o');pid=$PID;emulator_sha256=$digest;physical_access=$false;debugger=$true;ordinary_qualified=$false} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
  & (Join-Path $PSScriptRoot Invoke.ps1) -RunId nt5-bridge260-emu007 -InstanceTask windows-native-bridge260 `
   -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
   -Iso (Join-Path $ws outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
   -HddSource $f.fixture_path_windows -EepromSource (Join-Path $ws work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin) `
   -EmulatorPath $exe -EmulatorSha256 $digest -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 `
   -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 540
 }
}
