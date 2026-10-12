param([Parameter(Mandatory)][ValidateSet('control001','candidate001')][string]$Case)
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 64MB -lt 20GB -or (Get-PSDrive D).Free-2GB -lt 20GB){throw 'Projected20GiB space guard'}
$env:XWN301_CASE=$Case
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/hd-reservation301/prepare.py $env:XWN301_CASE
 if($LASTEXITCODE){throw '296 preparation failed'}
}
