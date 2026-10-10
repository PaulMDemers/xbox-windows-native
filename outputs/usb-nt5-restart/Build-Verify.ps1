$ErrorActionPreference='Stop'
$out="$PSScriptRoot/artifacts/verify001"
if(Test-Path $out){throw 'Never reuse verification build'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
 New-Item -ItemType Directory $out | Out-Null
 Copy-Item "$PSScriptRoot/verify.c","$PSScriptRoot/setup_gate201.h","$PSScriptRoot/restart_gate201.h" $out
 $linux=('/mnt/e'+$out.Substring(2)).Replace('\','/')
 $compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
 $args=@('-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-D_WIN32_WINNT=0x0500','-DNTDDI_VERSION=0x05000000','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0','-o',"$linux/verify.exe","$linux/verify.c",'-lkernel32','-luser32','-lsetupapi','-lhid','-ladvapi32')
 @{compiler=$compiler;arguments=$args;driver_rebuilt=$false;physical_access=$false}|ConvertTo-Json -Depth 4|Set-Content "$out/commands.json"
 & wsl -d Ubuntu -- $compiler @args 2>&1 | Tee-Object "$out/compiler.txt"
 if($LASTEXITCODE){throw 'Verification probe compile failed'}
}
