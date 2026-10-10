#requires -Version 7.4
$ErrorActionPreference='Stop'
$state=@{entered=$false}
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $state.entered=$true
            if((Get-PSDrive C).Free-128MB -lt 20GB){throw 'Projected C reserve guard'}
            & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207/archive-source001.sh
            if($LASTEXITCODE){throw 'Source archive failed; preserve attempt'}
        }
        exit 0
    } catch {
        if($state.entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Source archive prelaunch contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Source archive lease wait exhausted'
