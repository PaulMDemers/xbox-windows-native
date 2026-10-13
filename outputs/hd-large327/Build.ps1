#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('build001','build002','build003')][string]$Case)
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free-64MB -lt 20GB -or (Get-PSDrive D).Free-64MB -lt 20GB){throw '20GiB projected guard'}
$env:XWN327_BUILD=$Case
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/hd-large327/build.py $env:XWN327_BUILD
 if($LASTEXITCODE){throw 'Probe build failed; preserve this ID'}
}
