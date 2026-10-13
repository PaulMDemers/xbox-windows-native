#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free-64MB -lt 20GB -or (Get-PSDrive E).Free-64MB -lt 20GB){throw 'Projected20GiB guard'}
$dest='E:/xwn338/build001'
if(Test-Path $dest){throw 'Never repeat build001'}
New-Item -ItemType Directory $dest | Out-Null
foreach($name in @('wizard313.c','activation.inc','activation.h','policy.h','test-adapter.c')){Copy-Item (Join-Path $PSScriptRoot $name) $dest}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- bash -c 'set -e; cd /mnt/e/xwn338/build001; gcc -std=c11 -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer -g test-adapter.c -o host-test; ASAN_OPTIONS=detect_leaks=1 ./host-test > host-console.txt 2>&1; /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -DXWN_EMULATOR_ACTIVATION313=1 -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin -Wl,--entry,_mainCRTStartup@0 -Wl,--subsystem,console:5.0 -o wizard.exe wizard313.c -lkernel32 -luser32 > native-console.txt 2>&1'
 if($LASTEXITCODE){throw '313 build failed; preserve capsule'}
}
$pins=@{};Get-ChildItem $dest -File | ForEach-Object {$pins[$_.Name]=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()}
@{passed=$true;files=$pins;private=$dest;host_interfaces='Win32/process/log MODELS; actual adapter code';physical_access=$false;guest_launch=$false} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $PSScriptRoot build001.json)
Get-Content (Join-Path $dest host-console.txt)
