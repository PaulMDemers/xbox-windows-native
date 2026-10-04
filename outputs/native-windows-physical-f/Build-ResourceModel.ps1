#requires -Version 7.4
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-physical-f/build-resource-model.py *> (Join-Path $PSScriptRoot build-logs/resource-model.log)
 if ($LASTEXITCODE -ne 0) { throw 'Resource-model emulator build failed.' }
}
