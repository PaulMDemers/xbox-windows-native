#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 64MB -lt 20GB){throw '20GiB projected guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207/lifecycle001/prepare-emulator.py
 if($LASTEXITCODE){throw 'Resource rehearsal failed; preserve evidence'}
}
