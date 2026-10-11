#requires -Version 7.4
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 if((Get-PSDrive C).Free -lt 20GB){throw '20GiB unchanged guard'}
 $env:XWN_BUILD_LEASE='held'
 try { & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/surface-invalidation257/build001.py
 if($LASTEXITCODE){throw '257 build failed; preserve output'} } finally {Remove-Item Env:XWN_BUILD_LEASE}
}
