param([Parameter(Mandatory)][string]$Attempt)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$env:XWN632_ATTEMPT=$Attempt
$env:XWN632_KIT=$PSScriptRoot
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Python314/python.exe -B (Join-Path $env:XWN632_KIT 'build.py') $env:XWN632_ATTEMPT
    if ($LASTEXITCODE -ne 0) { throw '632 build failed' }
}
