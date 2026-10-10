param([Parameter(Mandatory)][ValidatePattern('^build[0-9]{3}$')][string]$Attempt,[ValidateRange(0,600)][int]$WaitSeconds=0)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-Content "$repo/.git/HEAD" -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-usb'){throw 'Wrong branch'}
if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
$out=Join-Path $PSScriptRoot "artifacts/$Attempt"
if((Test-Path $out) -or (Test-Path "$PSScriptRoot/$Attempt-failure.json")){throw 'Never reuse build attempt'}
$compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
$ddk='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/i686-w64-mingw32/include/ddk'
$linux=('/mnt/e'+$out.Substring(2)).Replace('\','/')
try {
 $deadline=[DateTime]::UtcNow.AddSeconds($WaitSeconds)
 $refusals=@()
 while($true) {
 try {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
  if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard after lease wait'}
  New-Item -ItemType Directory $out -ErrorAction Stop | Out-Null
  Copy-Item "$PSScriptRoot/setup_gate201.h","$PSScriptRoot/restart_gate201.h","$PSScriptRoot/driver.c","$PSScriptRoot/nt5hid.h","$PSScriptRoot/xid_hid.c","$PSScriptRoot/xid_hid.h","$PSScriptRoot/probe.c","$PSScriptRoot/xwnxid.inf" $out
  Copy-Item "$PSScriptRoot/../usb-xid-capture/driver-core/xid_wire.c","$PSScriptRoot/../usb-xid-capture/driver-core/xid_wire.h" $out
  $flags=@('-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-D_WIN32_WINNT=0x0500','-DNTDDI_VERSION=0x05000000')
  $driverArgs=$flags+@("-I$ddk",'-shared','-Wl,--entry,_DriverEntry@8','-Wl,--subsystem,native:5.0','-Wl,--image-base,0x10000','-Wl,--file-alignment,512','-Wl,--section-alignment,4096',"-Wl,-Map,$linux/driver.map",'-o',"$linux/xwnxid.sys","$linux/driver.c","$linux/xid_hid.c","$linux/xid_wire.c",'-lntoskrnl','-lhal','-lusbd','-lhidclass')
  $probeArgs=$flags+@('-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o',"$linux/probe.exe","$linux/probe.c",'-lkernel32','-luser32','-lsetupapi','-lhid','-ladvapi32')
  @{compiler=$compiler;driver_args=$driverArgs;probe_args=$probeArgs;physical_access=$false} | ConvertTo-Json -Depth 4 | Set-Content "$out/commands.json"
  & wsl -d Ubuntu -- $compiler @driverArgs 2>&1 | Tee-Object "$out/compiler-driver.txt"
  if($LASTEXITCODE){throw 'Driver compile failed'}
  & wsl -d Ubuntu -- $compiler @probeArgs 2>&1 | Tee-Object "$out/compiler-probe.txt"
  if($LASTEXITCODE){throw 'Probe compile failed'}
  & wsl -d Ubuntu -- sha256sum $compiler | Set-Content "$out/compiler-sha256.txt"
  & python -B "$PSScriptRoot/test_transport.py" $Attempt
  if($LASTEXITCODE){throw 'Transport fault tests failed'}
  $savedPath=$env:PATH
  try {
   $env:PATH='C:/msys64/mingw64/bin;'+$env:PATH
   & C:/msys64/mingw64/bin/gcc.exe -std=c11 -O2 -Wall -Wextra -Werror "-I$out" "$PSScriptRoot/test_hid.c" "$out/xid_hid.c" -o "$out/host-tests/hid.exe" 2>&1 | Tee-Object "$out/compiler-host.txt"
   if($LASTEXITCODE){throw 'Host mapping test compile failed'}
   & "$out/host-tests/hid.exe" | Tee-Object "$out/host-tests/hid-result.txt"
   if($LASTEXITCODE){throw 'Host mapping test failed'}
  } finally {$env:PATH=$savedPath}
 }
 break
 } catch {
  if($_.ToString() -match "Xbox resource 'build' is busy" -and [DateTime]::UtcNow -lt $deadline) {
   $refusals+=@{utc=[DateTime]::UtcNow.ToString('o');error=$_.ToString()}
   @{attempt=$Attempt;waiting=$true;refusals=$refusals} | ConvertTo-Json -Depth 4 | Set-Content "$PSScriptRoot/$Attempt-lease.json"
   Start-Sleep -Seconds 5
  } else {throw}
 }
 }
 @{attempt=$Attempt;waiting=$false;acquired=$true;refusals=$refusals} | ConvertTo-Json -Depth 4 | Set-Content "$PSScriptRoot/$Attempt-lease.json"
 @{compiled=$true;attempt=$Attempt;files=(Get-ChildItem $out -File | Get-FileHash | Select-Object Path,Hash);physical_access=$false;runtime_qualified=$false} | ConvertTo-Json -Depth 5 | Set-Content "$PSScriptRoot/$Attempt.json"
} catch {
 if(Test-Path "$PSScriptRoot/$Attempt-lease.json") {
  $lease=Get-Content "$PSScriptRoot/$Attempt-lease.json" -Raw | ConvertFrom-Json
  $lease.waiting=$false
  $lease | Add-Member -NotePropertyName ended_utc -NotePropertyValue ([DateTime]::UtcNow.ToString('o')) -Force
  $lease | Add-Member -NotePropertyName failure -NotePropertyValue $_.ToString() -Force
  $lease | ConvertTo-Json -Depth 5 | Set-Content "$PSScriptRoot/$Attempt-lease.json"
 }
 @{compiled=$false;attempt=$Attempt;error=$_.ToString();physical_access=$false} | ConvertTo-Json | Set-Content "$PSScriptRoot/$Attempt-failure.json"
 throw
}
