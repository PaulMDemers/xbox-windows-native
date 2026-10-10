#requires -Version 7.4
$ErrorActionPreference='Stop'
$state=@{entered=$false}
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $state.entered=$true
            if((Get-PSDrive C).Free-256MB -lt 20GB){throw 'Projected C reserve guard'}
            & python $PSScriptRoot/verify-source-archive001.py
            if($LASTEXITCODE){throw 'Source archive verification failed; preserve attempt'}
            & python $PSScriptRoot/package001.py
            if($LASTEXITCODE){throw 'Package assembly failed; preserve attempt'}
        }
        exit 0
    } catch {
        if($state.entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Package prelaunch contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Package lease wait exhausted'
