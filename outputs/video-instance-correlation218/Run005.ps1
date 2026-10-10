#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB -or (Get-PSDrive E).Free -lt 20GB){throw '20GiB guard'}
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$pins=Get-Content (Join-Path $PSScriptRoot emulator-frozen005.json) -Raw | ConvertFrom-Json
foreach($item in $pins.PSObject.Properties){if((Get-FileHash -LiteralPath $item.Name).Hash.ToLowerInvariant() -ne $item.Value){throw ('Frozen input changed '+$item.Name)}}
$f=Get-Content (Join-Path $PSScriptRoot emulator-inputs.json) -Raw | ConvertFrom-Json
if((Get-FileHash -LiteralPath $f.parent).Hash.ToLowerInvariant() -ne $f.parent_sha256){throw 'Parent changed'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  & (Join-Path $PSScriptRoot Invoke-218.ps1) -RunId stock-instance218-progress005 -InstanceTask windows-native-instance218 `
   -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
   -Iso (Join-Path $ws outputs/video-instance-correlation218/artifacts/build003/xwn-instance218.iso) `
   -HddSource $f.parent -EepromSource (Join-Path $ws work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin) `
   -EmulatorPath (Join-Path $ws outputs/xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe) `
   -EmulatorSha256 685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890 `
   -MonitorPort 4594 -GdbPort 4595 -CompactTrace -ManualCapture -RetainDisk -StopOnCaptureComplete -Seconds 120
 }
}
