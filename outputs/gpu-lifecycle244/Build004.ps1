#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20GiB build guard unchanged'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/gpu-lifecycle244/build004.py
 if($LASTEXITCODE -ne 0){throw '244 build failure preserved'}
}
if(Test-Path -LiteralPath (Join-Path $PSScriptRoot artifacts/build004)){throw 'Unique capsule already exists'}
New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot artifacts) -Force | Out-Null
New-Item -ItemType Junction -Path (Join-Path $PSScriptRoot artifacts/build004) -Target 'E:/Codex-archive/xbox-windows-native/phase244-build004' | Out-Null
