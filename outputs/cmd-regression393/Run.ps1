#requires -Version 7.4
param([ValidateSet('control001','candidate001')][string]$Case)
$ErrorActionPreference='Stop'
$out=Join-Path $PSScriptRoot $Case
if(Test-Path (Join-Path $out runner-start.json)){throw 'Unique run already consumed'}
$f=Get-Content (Join-Path $out fixture.json) -Raw | ConvertFrom-Json -AsHashtable
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$pins=Get-Content (Join-Path $out emulator-frozen.json) -Raw | ConvertFrom-Json
foreach($v in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $v.Name)).Hash.ToLowerInvariant() -ne $v.Value){throw ('Frozen input changed: '+$v.Name)}}
if((Get-FileHash $f.fixture_path_windows).Hash.ToLowerInvariant() -ne $f.fixture_sha256){throw 'Fixture hash mismatch'}
if((Get-PSDrive C).Free - (Get-Item $f.fixture_path_windows).Length - 2GB -lt 20GB){throw 'Projected C capacity guard'}
if(-not (Test-Path (Join-Path $PSScriptRoot close-host.py))){throw 'Close helper missing'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  @{utc=[DateTime]::UtcNow.ToString('o');physical_access=$false;debugger=$false} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
  & (Join-Path $PSScriptRoot Invoke.ps1) -RunId ("nt5-cmd393-"+$Case) -InstanceTask ("windows-native-cmd393-"+$Case) `
   -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
   -Iso (Join-Path $ws outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
   -HddSource $f.fixture_path_windows -EepromSource E:/xwn289/fixture001/hd.bin `
   -EmulatorPath E:/xwn329/retained-builds001/xemu-hd322.exe -EmulatorSha256 ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3 `
   -FtpPort 5338 -MonitorPort 5336 -GdbPort 5337 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -CaptureAudio -Seconds 1200
 }
}
