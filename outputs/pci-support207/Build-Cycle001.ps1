#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 64MB -lt 20GB){throw '20GiB projected guard'}
$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207'
$out=Join-Path $PSScriptRoot 'artifacts/cycle001'
if(Test-Path $out){throw 'Fresh cycle build required'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 ($p+'/extract-cycle-providers.py')
 if($LASTEXITCODE){throw 'Provider extraction failed'}
 New-Item -ItemType Directory $out | Out-Null
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/cycle001/cycle.exe') ($p+'/xwncycle.c') -lkernel32 -lsetupapi -luser32 -ladvapi32
 if($LASTEXITCODE){throw 'Cycle001 compile failure retained'}
}
@{scope='Emulator-only telemetry and guarded normal restart';source_sha256=(Get-FileHash (Join-Path $PSScriptRoot 'xwncycle.c')).Hash.ToLowerInvariant();sha256=(Get-FileHash (Join-Path $out 'cycle.exe')).Hash.ToLowerInvariant();physical_access=$false} | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot 'cycle001-build.json')
