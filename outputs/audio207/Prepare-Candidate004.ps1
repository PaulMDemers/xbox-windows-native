#requires -Version 7.4
$ErrorActionPreference='Stop'
$state=@{entered=$false}
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $state.entered=$true
            if((Get-PSDrive C).Free - 128MB -lt 20GB){throw 'Projected C reserve guard'}
            & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207/prepare-fixture004.py candidate004
            if($LASTEXITCODE){throw 'Candidate004 preparation failed; preserve attempt'}
        }
        exit 0
    } catch {
        if($state.entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Prepare prelaunch lease contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Preparation lease wait exhausted before work'
