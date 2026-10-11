#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20GiB build guard unchanged'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/gpu-reference-pair242/build003.py
 if($LASTEXITCODE -ne 0){throw 'Preserve227 build failure; inputs retained'}
}

if(-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot artifacts))){New-Item -ItemType Directory -Path (Join-Path $PSScriptRoot artifacts) | Out-Null}
if(Test-Path -LiteralPath (Join-Path $PSScriptRoot artifacts/build003)){throw 'Unique compiled capsule path already exists'}
New-Item -ItemType Junction -Path (Join-Path $PSScriptRoot artifacts/build003) -Target 'E:/Codex-archive/xbox-windows-native/phase242-build003' | Out-Null
