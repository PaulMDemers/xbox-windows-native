$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 & wsl -d Ubuntu -u paul -- env XBOX_XEMU_MODE=exclusive python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/perspective556/run001.py run --phase 1
 if($LASTEXITCODE){throw 'Owned VM supervisor failed; preserve state'}
}
