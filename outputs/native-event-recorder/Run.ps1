#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('001','002','003','004','005')][string]$Case)
$ErrorActionPreference='Stop'
$ws=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$f=Get-Content (Join-Path $PSScriptRoot ('fixture-'+$Case+'.json')) -Raw | ConvertFrom-Json
$b=Get-Content (Join-Path $PSScriptRoot build.json) -Raw | ConvertFrom-Json
$seed=Join-Path $ws ('work/native-event-recorder-'+$Case+'-seed.qcow2')
if ((Get-FileHash $seed).Hash -ne $f.seed_sha256) { throw 'Seed changed' }
$out=Join-Path $PSScriptRoot $Case
if ((Test-Path (Join-Path $ws ('work/runs/nt5-native-event-recorder-'+$Case))) -or (Test-Path (Join-Path $out host-config.json))) { throw 'Recorded attempt exists; never relaunch it.' }
New-Item -ItemType Directory -Force $out | Out-Null
$savedRecorder=$env:XWN_NATIVE_EVENT_LOG
try {
 Remove-Item Env:XWN_NATIVE_EVENT_LOG -ErrorAction SilentlyContinue
 if ($Case -ne '001') { $env:XWN_NATIVE_EVENT_LOG=Join-Path $out events.bin }
 @{case=$Case;recorder_enabled=($Case -ne '001');resource_model=$env:XWN_NV2A_RESOURCE_MODEL;emulator_sha256=$b.binary_sha256;gdb_attachment=$false;paused_capture=$false} | ConvertTo-Json | Set-Content (Join-Path $out host-config.json)
 & (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId ('nt5-native-event-recorder-'+$Case) `
  -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin `
  -Iso (Join-Path $PSScriptRoot ../native-windows-extended-storage/artifacts/f-boot-length-004.iso) `
  -HddSource $seed -EepromSource (Join-Path $ws work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin) `
  -EmulatorPath (Join-Path $PSScriptRoot artifacts/xemu-events.exe) -EmulatorSha256 $b.binary_sha256 `
  -CaptureWidth 1024 -CaptureHeight 576 -CapturePitch 4096 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 `
  -CompactTrace -UsbMouse -ManualCapture -RetainDisk -AllowGuestReboot -StopOnCaptureComplete -StopOnBugcheck -Seconds 600
} finally {
 if ($null -eq $savedRecorder) { Remove-Item Env:XWN_NATIVE_EVENT_LOG -ErrorAction SilentlyContinue }
 else { $env:XWN_NATIVE_EVENT_LOG=$savedRecorder }
}
