#requires -Version 7.4
$ErrorActionPreference='Stop'
if ((Get-PSDrive C).Free -lt 20GB) { throw '20GiB build guard' }
$root=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')
if (Test-Path (Join-Path $PSScriptRoot artifacts/probe.exe)) { throw 'Already built' }
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o "$root/artifacts/probe.exe" "$root/probe.c" -lkernel32 -luser32 -lgdi32 -ladvapi32 -lmsimg32
 if ($LASTEXITCODE -ne 0) { throw 'Probe build failed' }
}
