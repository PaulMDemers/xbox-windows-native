#requires -Version 7.4
$ErrorActionPreference='Stop'
$state=@{entered=$false}
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $state.entered=$true
            if((Get-PSDrive C).Free - 128MB -lt 20GB){throw 'Projected C reserve guard'}
            & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207/build-driver002.sh
            if($LASTEXITCODE){throw 'Build002 failed; preserve outputs and do not retry'}
        }
        exit 0
    } catch {
        if($state.entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Build prelaunch lease contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Build lease wait exhausted before work'
