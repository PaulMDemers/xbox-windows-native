#requires -Version 7.4
$ErrorActionPreference='Stop'
$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    if ((Get-PSDrive C).Free - 128MB -lt 20GB) { throw 'Projected 20 GiB C guard' }
    New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot artifacts/probe001) | Out-Null
    foreach($name in @('probe','runner')) {
        if(Test-Path (Join-Path $PSScriptRoot ('artifacts/probe001/'+$name+'.exe'))){throw 'Never overwrite binary'}
        & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -Wno-misleading-indentation -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/probe001/'+$name+'.exe') ($p+'/'+$name+'.c') -lkernel32 -luser32 -ladvapi32 -lwinmm
        if($LASTEXITCODE){throw ('Audio helper build failed: '+$name)}
    }
}
