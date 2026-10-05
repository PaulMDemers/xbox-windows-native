#requires -Version 7.4
param([ValidateSet('rename','cleanup','trace','deleted-write','rename-trace','rename-filter','unlinked')][string]$Variant='rename')
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot build-logs) | Out-Null
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-fatx-forensics/build-rename.sh $Variant *> (Join-Path $PSScriptRoot "build-logs/$Variant.log")
    if ($LASTEXITCODE -ne 0) { throw 'Rename integration build failed' }
}
