#requires -Version 7.4
$ErrorActionPreference='Stop'
$state=@{entered=$false}
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $state.entered=$true
            if((Get-PSDrive C).Free-128MB -lt 20GB){throw 'Projected C reserve guard'}
            $count=0
            Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.ps1' | ForEach-Object {
                $tokens=$null; $errors=$null
                [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName,[ref]$tokens,[ref]$errors)
                if($errors.Count){throw ('PowerShell syntax errors: '+$_.Name)}
                $count++
            }
            Write-Output ('PowerShell sources parsed: '+$count)
            & python $PSScriptRoot/final-review004.py
            if($LASTEXITCODE){throw 'Final source/package review failed; preserve attempt'}
            & python tools/check-repository.py
            if($LASTEXITCODE){throw 'Repository payload check failed'}
            & git diff --cached --check
            if($LASTEXITCODE){throw 'Staged whitespace check failed'}
        }
        exit 0
    } catch {
        if($state.entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Final review prelaunch contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Final review lease wait exhausted'
