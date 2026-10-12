param([Parameter(Mandatory)][string]$Attempt)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$env:XWN308_ATTEMPT=$Attempt
$env:XWN308_KIT=$PSScriptRoot
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Python314/python.exe -B (Join-Path $env:XWN308_KIT 'build.py') $env:XWN308_ATTEMPT
    if ($LASTEXITCODE -ne 0) { throw '308 build failed' }
}
