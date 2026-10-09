#requires -Version 7.4
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-Content -LiteralPath (Join-Path $repo '.git/HEAD') -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-pci'){throw 'Branch guard'}
if((& git -C $repo remote get-url origin) -ne 'https://github.com/PaulMDemers/xbox-windows-native.git'){throw 'Origin guard'}
if((Get-PSDrive C).Free - 64MB -lt 20GB){throw '20GiB projected guard'}
$out=Join-Path $PSScriptRoot 'artifacts/driver001'
if(Test-Path -LiteralPath $out){throw 'Fresh build required'}
$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207'
$ros='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    New-Item -ItemType Directory -Path $out | Out-Null
    & wsl -d Ubuntu -- ($ros+'/bin/i686-w64-mingw32-gcc') -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector -I ($ros+'/i686-w64-mingw32/include/ddk') '-Wl,--entry,_DriverEntry@8' '-Wl,--subsystem,native:5.0' '-Wl,--image-base,0x10000' '-Wl,--enable-reloc-section' '-Wl,--exclude-all-symbols,-file-alignment=0x1000,-section-alignment=0x1000' '-Wl,--wdmdriver' -shared -o ($p+'/artifacts/driver001/xwnsmb.sys') ($p+'/xwnsmb.c') -lntoskrnl -lhal
    if($LASTEXITCODE){throw 'Driver compile failure retained'}
    & wsl -d Ubuntu -- /home/paul/xbox-windows-native/build/hal-nt5/host-tools/bin/pefixup --wdmdriver ($p+'/artifacts/driver001/xwnsmb.sys')
    if($LASTEXITCODE){throw 'Driver PE fixup failure retained'}
    & wsl -d Ubuntu -- ($ros+'/bin/i686-w64-mingw32-gcc') -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/driver001/probe.exe') ($p+'/xwnsmb-probe.c') -lkernel32 -lsetupapi -lcfgmgr32
    if($LASTEXITCODE){throw 'Probe compile failure retained'}
    & wsl -d Ubuntu -- ($ros+'/bin/i686-w64-mingw32-gcc') -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/driver001/install.exe') ($p+'/xwnsmb-install.c') -lkernel32
    if($LASTEXITCODE){throw 'Installer compile failure retained'}
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot xwnsmb.inf) -Destination $out
@{scope='Experimental driver/probe compile only';physical_access=$false;guest_launch=$false;files=@(Get-ChildItem -LiteralPath $out -File | ForEach-Object { @{name=$_.Name;sha256=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()} });sources=@('smbus.h','xwnsmb.c','xwnsmb-probe.c','xwnsmb-install.c','xwnsmb.inf') | ForEach-Object { @{name=$_;sha256=(Get-FileHash (Join-Path $PSScriptRoot $_)).Hash.ToLowerInvariant()} }} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $PSScriptRoot 'driver001-build.json')
