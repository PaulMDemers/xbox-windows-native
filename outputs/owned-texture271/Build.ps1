param([Parameter(Mandatory)][string]$Attempt)
$ErrorActionPreference='Stop'
$env:PYTHONUTF8='1'
$env:XWN271_ATTEMPT=$Attempt
$env:XWN271_KIT=$PSScriptRoot
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Python314/python.exe -B (Join-Path $env:XWN271_KIT 'build.py') $env:XWN271_ATTEMPT
    if($LASTEXITCODE -ne 0) {throw "271 build failed: $LASTEXITCODE"}
}
