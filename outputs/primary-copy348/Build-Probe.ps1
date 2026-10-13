$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/primary-copy348/probe/build.py build001
 if($LASTEXITCODE -ne 0){throw 'Probe build failed; preserve attempt'}
}
