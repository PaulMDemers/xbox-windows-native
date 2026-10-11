#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 128MB -lt 20GB){throw '20GiB projected guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207/handoff001/build.py
 if($LASTEXITCODE){throw 'HAL handoff build failed; preserve attempt'}
}
