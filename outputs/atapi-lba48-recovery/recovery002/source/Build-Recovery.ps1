#requires -Version 7.4
$ErrorActionPreference='Stop'
if ((Get-PSDrive C).Free -lt 20GB) { throw '20GiB build guard' }
$root=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')
$output=Join-Path $PSScriptRoot artifacts/recovery-probe.exe
if (Test-Path $output) { throw 'Recovery helper already built' }
& 'C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1' -Resource build -Action {
    & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc `
      -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin `
      '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' `
      -o "$root/artifacts/recovery-probe.exe" "$root/recovery-probe.c" -lkernel32 -ladvapi32 -luser32
    if ($LASTEXITCODE -ne 0) { throw 'Recovery helper build failed' }
}
