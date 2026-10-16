#requires -Version 7.4
$ErrorActionPreference='Stop'
$out=Join-Path $PSScriptRoot emu001
if(Test-Path (Join-Path $out runner-start.json)){throw 'Consumed run ID'}
$f=Get-Content (Join-Path $PSScriptRoot '../handoff-trace412/preparation002.json') -Raw | ConvertFrom-Json
if(-not $f.prepared){throw 'Assembly not verified'}
if((Get-FileHash 'E:/xwn412/preparation002/fresh.qcow2').Hash.ToLowerInvariant() -ne $f.fixture_sha256){throw 'Assembly changed'}
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$pins=Get-Content (Join-Path $out frozen.json) -Raw | ConvertFrom-Json
foreach($v in $pins.PSObject.Properties){if((Get-FileHash (Join-Path $ws $v.Name)).Hash.ToLowerInvariant() -ne $v.Value){throw ('Frozen input changed: '+$v.Name)}}
if((Get-PSDrive C).Free-16MB -lt 20GB -or (Get-PSDrive E).Free-128MB -lt 20GB){throw 'Projected runtime reserve'}
$portable='E:/xwn405/instances/windows-native-fresh405-emu001/EA3473314E6C0EA0/xemu-windows-native-fresh405-emu001.exe'
if((Get-FileHash $portable).Hash.ToLowerInvariant() -ne 'ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'){throw 'Reused closed portable changed'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 @{utc=[DateTime]::UtcNow.ToString('o');physical_access=$false;debugger=$true;fresh_overlay=$true} | ConvertTo-Json | Set-Content (Join-Path $out runner-start.json)
 & (Join-Path $PSScriptRoot Invoke.ps1) -RunId nt5-cromwell413-emu001 -InstanceTask windows-native-fresh405-emu001 `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
 -Iso (Join-Path $ws outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
 -HddSource 'E:/xwn412/preparation002/fresh.qcow2' -EepromSource E:/xwn289/fixture001/hd.bin `
 -EmulatorPath E:/xwn329/retained-builds001/xemu-hd322.exe -EmulatorSha256 ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3 `
 -FtpPort 5492 -MonitorPort 5490 -GdbPort 5491 -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 240
}
