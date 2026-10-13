#requires -Version 7.4
$ErrorActionPreference='Stop'
& C:/Python314/python.exe -B (Join-Path $PSScriptRoot preflight-capacity003.py)
if($LASTEXITCODE){throw 'Dependency preflight failed'}
$f=Get-Content (Join-Path $PSScriptRoot capacity-emu003/fixture.json) -Raw | ConvertFrom-Json
if((Get-FileHash $f.fixture_path_windows).Hash.ToLowerInvariant() -ne $f.fixture_sha256){throw 'Fixture changed'}
if((Get-PSDrive C).Free - 64MB -lt 20GB -or (Get-PSDrive E).Free - (Get-Item $f.fixture_path_windows).Length - 512MB -lt 20GB){throw 'Space guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  & (Join-Path $PSScriptRoot InvokeCapacity003.ps1) -RunId nt5-capacity333-emu003 -InstanceTask windows-native-cap333-emu003 `
   -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
   -Iso (Join-Path $PSScriptRoot ../native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
   -HddSource $f.fixture_path_windows -EepromSource E:/xwn289/fixture001/hd.bin `
   -EmulatorPath E:/xwn329/retained-builds001/xemu-hd322.exe -EmulatorSha256 ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3 `
   -FtpPort 5118 -MonitorPort 5116 -GdbPort 5117 -CompactTrace -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -Seconds 180
 }
}
