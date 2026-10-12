param([Parameter(Mandatory)][ValidateSet('control001','candidate001')][string]$Case)
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 64MB -lt 20GB -or (Get-PSDrive E).Free-2GB -lt 20GB){throw 'Projected20GiB space guard'}
$env:XWN296_CASE=$Case
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/launcher-windows296/prepare.py $env:XWN296_CASE
 if($LASTEXITCODE){throw '296 preparation failed'}
}
