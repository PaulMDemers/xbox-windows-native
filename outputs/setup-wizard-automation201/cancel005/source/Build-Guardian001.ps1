#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB guard'}
$p='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/setup-wizard-automation201'
$dest=Join-Path $PSScriptRoot artifacts/guardian001
if(Test-Path $dest){throw 'Never overwrite guardian001'}
New-Item -ItemType Directory $dest | Out-Null
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- gcc -std=c11 -O1 -g -Wall -Wextra -Werror '-fsanitize=address,undefined' -o ($p+'/artifacts/guardian001/test-restart') ($p+'/test-restart201.c')
 if($LASTEXITCODE){throw 'Host compile failed'}
 & wsl -d Ubuntu -- ($p+'/artifacts/guardian001/test-restart')
 if($LASTEXITCODE){throw 'Host guard tests failed'}
 & wsl -d Ubuntu -- gcc -std=c11 -O1 -g -Wall -Wextra -Werror '-fsanitize=address,undefined' -o ($p+'/artifacts/guardian001/test-setup') ($p+'/test-setup201.c')
 if($LASTEXITCODE){throw 'Host setup compile failed'}
 & wsl -d Ubuntu -- ($p+'/artifacts/guardian001/test-setup')
 if($LASTEXITCODE){throw 'Host setup tests failed'}
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/guardian001/guardian.exe') ($p+'/guardian201.c') -lkernel32 -luser32 -ladvapi32
 if($LASTEXITCODE){throw 'Guardian failed; preserve source'}
}
@{built=$true;host_restart_tests=$true;source_sha256=(Get-FileHash (Join-Path $PSScriptRoot guardian201.c)).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash (Join-Path $dest guardian.exe)).Hash.ToLowerInvariant();physical_access=$false;guest_launch=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot guardian-build001.json)
