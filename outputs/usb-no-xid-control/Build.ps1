param([ValidatePattern('^build[0-9]{3}$')][string]$Attempt='build001')
$ErrorActionPreference='Stop'
$out="$PSScriptRoot/artifacts/$Attempt"
if(Test-Path $out){throw 'Never reuse build attempt'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
 New-Item -ItemType Directory $out | Out-Null
 Copy-Item "$PSScriptRoot/control.c","$PSScriptRoot/wizard006.c","$PSScriptRoot/policy.h","$PSScriptRoot/setup_gate201.h","$PSScriptRoot/restart_gate201.h","$PSScriptRoot/test-policy.c" $out
 $linux=('/mnt/e'+$out.Substring(2)).Replace('\','/')
 $compiler='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
 $flags=@('-Os','-Wall','-Wextra','-Werror','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0')
 $control=$flags+@('-o',"$linux/control.exe","$linux/control.c",'-lkernel32','-luser32','-ladvapi32')
 $wizard=$flags+@('-o',"$linux/wizard.exe","$linux/wizard006.c",'-lkernel32','-luser32')
 @{compiler=$compiler;control=$control;wizard=$wizard;physical_access=$false}|ConvertTo-Json -Depth 4|Set-Content "$out/commands.json"
 wsl -d Ubuntu -- $compiler @control 2>&1 | Tee-Object "$out/control-compiler.txt"
 if($LASTEXITCODE){throw 'Control build failed'}
 wsl -d Ubuntu -- $compiler @wizard 2>&1 | Tee-Object "$out/wizard-compiler.txt"
 if($LASTEXITCODE){throw 'Wizard build failed'}
 $saved=$env:PATH
 try {
  $env:PATH='C:/msys64/mingw64/bin;'+$env:PATH
  & C:/msys64/mingw64/bin/gcc.exe -O2 -Wall -Wextra -Werror "$out/test-policy.c" -o "$out/policy-test.exe"
  if($LASTEXITCODE){throw 'Policy test compile failed'}
  & "$out/policy-test.exe" | Tee-Object "$out/policy-result.txt"
  if($LASTEXITCODE){throw 'Policy test failed'}
 } finally {$env:PATH=$saved}
}
