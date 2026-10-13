$ErrorActionPreference = 'Stop'
& 'C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1' -Resource build -Action {
    & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/bandwidth364/build.py
    if ($LASTEXITCODE -ne 0) { throw '364 build failed; preserve consumed attempt' }
}
