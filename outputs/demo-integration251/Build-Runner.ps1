#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 128MB -lt 20GB){throw 'Projected 20GiB reserve'}
$out=Join-Path $PSScriptRoot artifacts/build001
if(Test-Path $out){throw 'Preserve completed/failed build; never rebuild in place'}
New-Item -ItemType Directory -Path $out | Out-Null
$p=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/build001/runner.exe') ($p+'/runner.c') -lkernel32 -luser32 -ladvapi32
 if($LASTEXITCODE){throw 'Build failed; preserve attempt'}
}
@{compiled=$true;source_sha256=(Get-FileHash (Join-Path $PSScriptRoot runner.c)).Hash.ToLowerInvariant();binary_sha256=(Get-FileHash (Join-Path $out runner.exe)).Hash.ToLowerInvariant();guest_launch=$false;physical_access=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot runner-build001.json)
