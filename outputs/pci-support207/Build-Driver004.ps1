#requires -Version 7.4
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-Content -LiteralPath (Join-Path $repo '.git/HEAD') -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-pci'){throw 'Branch guard'}
if((& git -C $repo remote get-url origin) -ne 'https://github.com/PaulMDemers/xbox-windows-native.git'){throw 'Origin guard'}
if((Get-PSDrive C).Free - 64MB -lt 20GB){throw '20GiB projected guard'}
$out=Join-Path $PSScriptRoot 'artifacts/driver004'
if(Test-Path -LiteralPath $out){throw 'Fresh build required'}
$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207'
$ros='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386'
$kernel=Join-Path $PSScriptRoot 'artifacts/driver003/xwnsmb.sys'
$kernelHash='15dba6948fd9184d09d94a4ab1517c2b86e8497af0e361b41359d1c20fc8057e'
if((Get-FileHash $kernel).Hash.ToLowerInvariant() -ne $kernelHash){throw 'Compiled003 kernel changed'}
foreach($name in @('xwnsmb003.c','smbus.h','constraints.h')){
 if((Get-FileHash (Join-Path $PSScriptRoot $name)).Hash -ne (Get-FileHash (Join-Path $PSScriptRoot ('artifacts/driver003/'+$name))).Hash){throw 'Compiled003 source changed'}
}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    New-Item -ItemType Directory -Path $out | Out-Null
    Copy-Item $kernel -Destination (Join-Path $out 'xwnsmb.sys')
    & wsl -d Ubuntu -- ($ros+'/bin/i686-w64-mingw32-gcc') -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/driver004/probe.exe') ($p+'/xwnsmb-probe.c') -lkernel32 -lsetupapi -lcfgmgr32
    if($LASTEXITCODE){throw 'Probe compile failure retained'}
    & wsl -d Ubuntu -- ($ros+'/bin/i686-w64-mingw32-gcc') -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/driver004/install.exe') ($p+'/xwnsmb-install.c') -lkernel32
    if($LASTEXITCODE){throw 'Installer compile failure retained'}
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot xwnsmb.inf) -Destination $out
@{scope='Reuse pinned003 constrained kernel; compile004 probe/installer';physical_access=$false;guest_launch=$false;files=@(Get-ChildItem -LiteralPath $out -File | ForEach-Object { @{name=$_.Name;sha256=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()} });sources=@('smbus.h','constraints.h','xwnsmb003.c','xwnsmb-probe.c','xwnsmb-install.c','xwnsmb.inf') | ForEach-Object { @{name=$_;sha256=(Get-FileHash (Join-Path $PSScriptRoot $_)).Hash.ToLowerInvariant()} }} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $PSScriptRoot 'driver004-build.json')
