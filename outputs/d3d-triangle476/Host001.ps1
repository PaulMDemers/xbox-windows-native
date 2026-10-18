#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free-32MB -lt 20GB){throw 'Projected reserve guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/d3d-triangle476/host001.py
 if($LASTEXITCODE){throw 'Build failed; preserve attempt'}
}
