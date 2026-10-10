#requires -Version 7.4
$ErrorActionPreference='Stop'
$entered=$false
for($attempt=1;$attempt -le 30;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $script:entered=$true
            if((Get-PSDrive C).Free-128MB -lt 20GB){throw 'Projected C reserve guard'}
            & python $PSScriptRoot/freeze001.py
            if($LASTEXITCODE){throw 'Physical freeze failed; preserve attempt'}
        }
        exit 0
    } catch {
        if($entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Freeze lease contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Freeze lease wait exhausted'
