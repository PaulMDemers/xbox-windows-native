#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB build guard'}
$p='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-observation188'
$dest=Join-Path $PSScriptRoot artifacts/build002
if(Test-Path $dest){throw 'Never overwrite or repeat build002'}
New-Item -ItemType Directory $dest | Out-Null
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/build002/observer.exe') ($p+'/probe002.c') -lkernel32 -luser32 -lsetupapi -lcfgmgr32
 if($LASTEXITCODE){throw 'Observer build002 failed; preserve attempt'}
}
@{built=$true;source_sha256=(Get-FileHash (Join-Path $PSScriptRoot probe002.c)).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash (Join-Path $dest observer.exe)).Hash.ToLowerInvariant();physical_access=$false;guest_launch=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot build002.json)
