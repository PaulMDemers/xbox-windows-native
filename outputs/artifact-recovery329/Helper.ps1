$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/artifact-recovery329/helper.py
 if($LASTEXITCODE){throw 'Helper reconstruction failed; preserve attempt'}
}
