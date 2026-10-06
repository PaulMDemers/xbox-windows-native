#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot artifacts) | Out-Null
foreach($name in @('probe','matched')) {
$source=(Join-Path $PSScriptRoot ($name+'.c')).Replace('\','/').Replace('C:','/mnt/c')
$output=(Join-Path $PSScriptRoot ('artifacts/'+$name+'.exe')).Replace('\','/').Replace('C:','/mnt/c')
& 'C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1' -Resource build -Action {
    & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc `
        -Os -Wall -Wextra -Werror -nostdlib -fno-stack-protector -fno-builtin `
        '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o $output $source -lkernel32 -ladvapi32 -luser32
    if($LASTEXITCODE -ne 0){throw 'NT5 probe compilation failed'}
}
}
