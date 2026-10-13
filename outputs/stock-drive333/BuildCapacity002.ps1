#requires -Version 7.4
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Python314/python.exe -B (Join-Path $PSScriptRoot build-capacity002.py)
 if($LASTEXITCODE){throw 'Capacity build failed; preserve attempt'}
}
