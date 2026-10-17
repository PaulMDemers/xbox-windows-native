param([Parameter(Mandatory)][string]$Attempt)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$env:XWN430_ATTEMPT=$Attempt
$env:XWN430_KIT=$PSScriptRoot
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Python314/python.exe -B (Join-Path $env:XWN430_KIT 'build.py') $env:XWN430_ATTEMPT
    if ($LASTEXITCODE -ne 0) { throw '430 build failed' }
}
