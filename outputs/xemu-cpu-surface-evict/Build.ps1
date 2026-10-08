#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB build guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/xemu-cpu-surface-evict/build.py
    if($LASTEXITCODE -ne 0){throw 'Matched xemu build failed; preserve evidence'}
}
