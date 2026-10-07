#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if ((Get-PSDrive C).Free -lt 20GB) { throw 'Preserved20GiB build guard' }
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot artifacts) | Out-Null
$root=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')
& 'C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1' -Resource build -Action {
  $gcc='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
  & wsl -d Ubuntu -- $gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin `
    '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o "$root/artifacts/probe.exe" "$root/probe.c" -lkernel32 -ladvapi32
  if ($LASTEXITCODE -ne 0) { throw 'Probe build failed' }
  & wsl -d Ubuntu -- $gcc -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin `
    '-I/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/i686-w64-mingw32/include/ddk' `
    -D_WIN32_WINNT=0x0500 -DNTDDI_VERSION=0x05000000 -shared '-Wl,--entry,_DriverEntry@8' `
    '-Wl,--subsystem,native:5.0' '-Wl,--image-base,0x10000' '-Wl,--file-alignment,512' '-Wl,--section-alignment,4096' `
    -o "$root/artifacts/trigger.sys" "$root/trigger.c" /home/paul/xbox-windows-native/build/fatx-dump-map-001/build-fatx/ntoskrnl/CMakeFiles/libntoskrnl.dir/libntoskrnl.a
  if ($LASTEXITCODE -ne 0) { throw 'Trigger build failed' }
}
