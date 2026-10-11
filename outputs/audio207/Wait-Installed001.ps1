#requires -Version 7.4
param([ValidateSet('installed001')][string]$Case)
$ErrorActionPreference='Stop'
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & (Join-Path $PSScriptRoot Run-Installed001.ps1) -Case $Case
        exit 0
    } catch {
        if((Test-Path (Join-Path $PSScriptRoot "$Case/runner-start.json")) -or $_.Exception.Message -notlike "Xbox resource '*' is busy or unavailable*"){throw}
        Write-Output ('Prelaunch lease contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Bounded lease wait exhausted without guest launch'
