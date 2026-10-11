#requires -Version 7.4
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
if((Get-Content (Join-Path $repo '.git/HEAD') -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-pci'){throw 'Branch guard'}
if((Get-PSDrive C).Free - 64MB -lt 20GB){throw '20GiB projected guard'}
$out=Join-Path $PSScriptRoot 'artifacts/build001'
if(Test-Path $out){throw 'Fresh build required'}
$root='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207/hardware220'
$gcc='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 $pin=& wsl -d Ubuntu -- sha256sum $gcc
 if($LASTEXITCODE -or $pin -notmatch '^83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5 '){throw 'Compiler pin'}
 New-Item -ItemType Directory -Path $out | Out-Null
 Copy-Item (Join-Path $PSScriptRoot 'inventory.c') $out
 & wsl -d Ubuntu -- $gcc -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($root+'/artifacts/build001/inventory.exe') ($root+'/inventory.c') -lkernel32 -lsetupapi -lcfgmgr32
 if($LASTEXITCODE){throw 'Inventory001 compile failed; preserve source/artifacts'}
}
$observer='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/device-observation188/artifacts/build003/observer.exe'
if((Get-FileHash $observer).Hash.ToLowerInvariant() -ne 'd69deda03c943de6d9aa10f76eebaf4474c09368c60a639cbb49c1add7be1487'){throw 'Observer pin'}
Copy-Item $observer $out
@{scope='Read-only NT5 user-mode PCI inventory and unchanged passive188 observer';physical_access=$false;compiler_sha256='83015512671faaa0dbe6f043a0107f79c049f4268a67e39955388a8d9a0182e5';files=@(Get-ChildItem $out -File | ForEach-Object {@{name=$_.Name;sha256=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()}})} | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $PSScriptRoot 'build001.json')
