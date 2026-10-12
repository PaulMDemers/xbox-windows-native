$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Python314/python.exe -B (Join-Path $PSScriptRoot 'prepare.py') emu001
 if($LASTEXITCODE -ne 0){throw 'Preparation failed'}
}
