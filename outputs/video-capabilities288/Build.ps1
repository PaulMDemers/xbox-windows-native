param([Parameter(Mandatory)][string]$Attempt)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$env:XWN288_ATTEMPT=$Attempt
$env:XWN288_KIT=$PSScriptRoot
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Python314/python.exe -B (Join-Path $env:XWN288_KIT 'build.py') $env:XWN288_ATTEMPT
    if ($LASTEXITCODE -ne 0) { throw '288 build failed' }
}
