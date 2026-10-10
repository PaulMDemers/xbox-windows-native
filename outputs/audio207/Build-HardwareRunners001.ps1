#requires -Version 7.4
$ErrorActionPreference='Stop'
$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207'
$state=@{entered=$false}
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $state.entered=$true
            if((Get-PSDrive C).Free-128MB -lt 20GB){throw 'Projected C reserve guard'}
            if(Test-Path (Join-Path $PSScriptRoot artifacts/hardwarehelpers001)){throw 'Preserve previous hardware runner build'}
            New-Item -ItemType Directory (Join-Path $PSScriptRoot artifacts/hardwarehelpers001) | Out-Null
            foreach($name in @('physical-install-runner','physical-playback-runner')) {
                & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -Wall -Wextra -Werror -Wno-misleading-indentation -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o ($p+'/artifacts/hardwarehelpers001/'+$name+'.exe') ($p+'/'+$name+'.c') -lkernel32 -luser32 -ladvapi32 -lsetupapi -lwinmm
                if($LASTEXITCODE){throw ('Hardware runner helper build failed: '+$name)}
            }
        }
        exit 0
    } catch {
        if($state.entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Hardware runner build prelaunch contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Hardware runner build lease wait exhausted'
