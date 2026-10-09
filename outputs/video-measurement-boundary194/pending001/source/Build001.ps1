#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB build guard'}
$taskPath='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/video-measurement-boundary194'
$taskArtifacts=Join-Path $PSScriptRoot artifacts/build001
if(Test-Path $taskArtifacts){throw 'Never overwrite a build attempt'}
New-Item -ItemType Directory $taskArtifacts | Out-Null
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- gcc -O1 -g -Wall -Wextra -Werror '-fsanitize=address,undefined' ($taskPath+'/test-setup.c') -o ($taskPath+'/artifacts/build001/test-setup')
 if($LASTEXITCODE){throw 'Setup gate host build failed'}
 & wsl -d Ubuntu -- env ASAN_OPTIONS=detect_leaks=1 ($taskPath+'/artifacts/build001/test-setup')
 if($LASTEXITCODE){throw 'Setup gate host test failed'}
 & wsl -d Ubuntu -- gcc -O1 -g -Wall -Wextra -Werror '-fsanitize=address,undefined' ($taskPath+'/test-restart.c') -o ($taskPath+'/artifacts/build001/test-restart')
 if($LASTEXITCODE){throw 'Original restart gate host build failed'}
 & wsl -d Ubuntu -- env ASAN_OPTIONS=detect_leaks=1 ($taskPath+'/artifacts/build001/test-restart')
 if($LASTEXITCODE){throw 'Original restart gate host test failed'}
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($taskPath+'/artifacts/build001/runner.exe') ($taskPath+'/runner.c') -lkernel32 -ladvapi32 -luser32
 if($LASTEXITCODE){throw 'Runner build failed'}
}
@{built=$true;host_tests=$true;setup_cases=8011;restart_cases=8;source_sha256=(Get-FileHash (Join-Path $PSScriptRoot runner.c)).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash (Join-Path $taskArtifacts runner.exe)).Hash.ToLowerInvariant();physical_access=$false;guest_launch=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot build001.json)
