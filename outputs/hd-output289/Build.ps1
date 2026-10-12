param([Parameter(Mandatory)][string]$Attempt)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$env:XWN289_ATTEMPT=$Attempt
$env:XWN289_KIT=$PSScriptRoot
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Python314/python.exe -B (Join-Path $env:XWN289_KIT 'build.py') $env:XWN289_ATTEMPT
    if ($LASTEXITCODE -ne 0) { throw '289 build failed' }
}
