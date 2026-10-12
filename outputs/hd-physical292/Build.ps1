param([Parameter(Mandatory)][string]$Attempt)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$env:XWN292_ATTEMPT=$Attempt
$env:XWN292_KIT=$PSScriptRoot
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Python314/python.exe -B (Join-Path $env:XWN292_KIT 'build.py') $env:XWN292_ATTEMPT
    if ($LASTEXITCODE -ne 0) { throw '292 build failed' }
}
