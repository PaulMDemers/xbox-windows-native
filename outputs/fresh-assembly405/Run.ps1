#requires -Version 7.4
$ErrorActionPreference='Stop'
$out=Join-Path $PSScriptRoot emu001
if(Test-Path (Join-Path $out runner-start.json)){throw 'Consumed run ID'}
$f=Get-Content (Join-Path $PSScriptRoot assembly001.json) -Raw | ConvertFrom-Json
if($f.status -ne 'assembled-readback-verified'){throw 'Assembly not verified'}
if((Get-FileHash $f.fixture_path_windows).Hash.ToLowerInvariant() -ne $f.fixture_sha256){throw 'Assembly changed'}
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$pins=Get-Content (Join-Path $out frozen.json) -Raw | ConvertFrom-Json
foreach($v in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $v.Name)).Hash.ToLowerInvariant() -ne $v.Value){throw ('Frozen input changed: '+$v.Name)}}
if((Get-PSDrive C).Free-256MB -lt 20GB -or (Get-PSDrive E).Free-220MB -lt 20GB){throw 'Projected runtime reserve'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 @{utc=[DateTime]::UtcNow.ToString('o');physical_access=$false;debugger=$false;fresh_overlay=$true} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
 & (Join-Path $PSScriptRoot Invoke.ps1) -RunId nt5-fresh405-emu001 -InstanceTask windows-native-fresh405-emu001 `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
 -Iso (Join-Path $ws outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
 -HddSource $f.fixture_path_windows -EepromSource E:/xwn289/fixture001/hd.bin `
 -EmulatorPath E:/xwn329/retained-builds001/xemu-hd322.exe -EmulatorSha256 ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3 `
 -FtpPort 5458 -MonitorPort 5456 -GdbPort 5457 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 600
}
