#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw 'Unchanged20GiB guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -u root -e bash -lc 'export XWN_BUILD_LEASE=held; export PYTHONDONTWRITEBYTECODE=1; python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/worker-barrier247/build002.py'
 if($LASTEXITCODE -ne 0){throw '247 build failed; preserve record and do not replay'}
}
