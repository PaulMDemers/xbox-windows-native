#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 32MB -lt 20GB){throw 'Projected reserve guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/marker-handoff466/stub-host001.py
 if($LASTEXITCODE){throw 'Host test failed; preserve attempt'}
}
