#requires -Version 7.4
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot build-logs) | Out-Null
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-event-recorder/build.py *> (Join-Path $PSScriptRoot build-logs/build.log)
 if ($LASTEXITCODE -ne 0) { throw 'Event recorder build failed; see build log.' }
}
