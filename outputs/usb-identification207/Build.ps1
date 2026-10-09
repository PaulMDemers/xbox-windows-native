#requires -Version 7.4
param([Parameter(Mandatory)][ValidatePattern('^build[0-9]{3}$')][string]$Attempt)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-Content "$repo/.git/HEAD" -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-usb'){throw 'Wrong branch'}
if((& git -C $repo config --get remote.origin.url).Trim() -ne 'https://github.com/PaulMDemers/xbox-windows-native.git'){throw 'Wrong origin'}
if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
$out=Join-Path $PSScriptRoot "artifacts/$Attempt"
$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/usb/repo/outputs/usb-identification207'
$compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 New-Item -ItemType Directory $out -ErrorAction Stop | Out-Null
 Copy-Item (Join-Path $PSScriptRoot probe.c) (Join-Path $out probe.c)
 & wsl -d Ubuntu -- $compiler -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/'+$Attempt+'/usbprobe.exe') ($p+'/artifacts/'+$Attempt+'/probe.c') -lkernel32 -luser32 -lsetupapi -lcfgmgr32 2>&1 | Tee-Object (Join-Path $out compiler.txt)
 if($LASTEXITCODE){throw 'Compile failed; preserved attempt'}
}
@{compiled=$true;physical_access=$false;runtime_qualified=$false;source_sha256=(Get-FileHash "$out/probe.c").Hash.ToLowerInvariant();binary_sha256=(Get-FileHash "$out/usbprobe.exe").Hash.ToLowerInvariant();compiler=$compiler;compiler_sha256=((& wsl -d Ubuntu -- sha256sum $compiler) -split ' ')[0]} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot "$Attempt.json")
