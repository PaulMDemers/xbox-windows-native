param([Parameter(Mandatory)][ValidateSet('control004','candidate004')][string]$Mode)
$ErrorActionPreference='Stop'
# Fresh ext4 source uses C backing; output/temp remain E. Reserve 256 MiB C.
if((Get-PSDrive C).Free - 256MB -lt 20GB){throw '20GiB projected C guard'}
if((Get-PSDrive E).Free -lt 1GB){throw 'E build headroom'}
$env:XWN293_MODE=$Mode
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/launcher-relocation293/build.py $env:XWN293_MODE
 if($LASTEXITCODE -ne 0){throw '293 build failed'}
}
