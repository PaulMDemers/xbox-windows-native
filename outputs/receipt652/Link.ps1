$ErrorActionPreference = 'Stop'
& 'C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1' -Resource build -Action {
    wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/receipt652/link.py
    if ($LASTEXITCODE -ne 0) { throw '652 link failed; preserve linked001.json' }
}
