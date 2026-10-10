#requires -Version 7.4
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../..'))
$git='C:/Program Files/Git/cmd/git.exe'
if((& $git -c "safe.directory=$repo" -C $repo branch --show-current) -ne 'codex/xbox-native-pci'){throw 'Branch guard'}
if((Get-PSDrive C).Free - 32MB -lt 20GB){throw '20GiB projected guard'}
$out=Join-Path $PSScriptRoot 'artifacts/build001'
if(Test-Path -LiteralPath $out){throw 'Fresh build required'}
$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207/lifecycle001'
$ros='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 New-Item -ItemType Directory -Path $out -Force | Out-Null
 & wsl -d Ubuntu -- ($ros+'/bin/i686-w64-mingw32-gcc') -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector -I ($ros+'/i686-w64-mingw32/include/ddk') '-Wl,--entry,_DriverEntry@8' '-Wl,--subsystem,native:5.0' '-Wl,--image-base,0x10000' '-Wl,--enable-reloc-section' '-Wl,--exclude-all-symbols,-file-alignment=0x1000,-section-alignment=0x1000' '-Wl,--wdmdriver' -shared -o ($p+'/artifacts/build001/xwnrsc.sys') ($p+'/xwnrsc.c') -lntoskrnl -lhal
 if($LASTEXITCODE){throw 'Kernel compile failed; preserve attempt'}
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/build/hal-nt5/host-tools/bin/pefixup --wdmdriver ($p+'/artifacts/build001/xwnrsc.sys')
 if($LASTEXITCODE){throw 'PE fixup failed'}
 foreach($name in @('install','probe')) {
  & wsl -d Ubuntu -- ($ros+'/bin/i686-w64-mingw32-gcc') -Os -Wall -Wextra -Werror -nostdlib -fno-builtin -fno-stack-protector '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/build001/'+$name+'.exe') ($p+'/'+$name+'.c') -lkernel32 -lsetupapi -lcfgmgr32 -ladvapi32 -luser32
  if($LASTEXITCODE){throw "Helper compile failed: $name; preserve attempt"}
 }
 & wsl -d Ubuntu -- sha256sum ($ros+'/bin/i686-w64-mingw32-gcc') | Set-Content (Join-Path $PSScriptRoot 'compiler001.txt')
}
@{scope='Resource-only genuine PnP trial; no bus transactions';physical_access=$false;files=@(Get-ChildItem -LiteralPath $out -File | ForEach-Object {@{name=$_.Name;sha256=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()}});sources=@(Get-ChildItem -LiteralPath $PSScriptRoot -File | Where-Object {$_.Extension -in '.c','.h','.inf','.ps1','.py'} | ForEach-Object {@{name=$_.Name;sha256=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()}})} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $PSScriptRoot 'build001.json')
