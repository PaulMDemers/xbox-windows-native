#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 1GB -lt 20GB -or (Get-PSDrive E).Free - 256MB -lt 20GB){throw 'Build capacity guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/stock-boot334/build.py
 if($LASTEXITCODE){throw 'Stock E build failed; preserve attempt'}
}
