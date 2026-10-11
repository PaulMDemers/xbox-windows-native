#requires -Version 7.4
$ErrorActionPreference='Stop'
if ((Get-PSDrive C).Free -lt 20GB) { throw '20GiB build guard' }
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/frontend-close246/build.py
 if ($LASTEXITCODE -ne 0) { throw '246 build failure preserved' }
}
New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot artifacts) -Force | Out-Null
if (Test-Path (Join-Path $PSScriptRoot artifacts/build001)) { throw 'Unique build already exists' }
New-Item -ItemType Junction -Path (Join-Path $PSScriptRoot artifacts/build001) -Target E:/Codex-archive/xbox-windows-native/phase246-build001 | Out-Null
