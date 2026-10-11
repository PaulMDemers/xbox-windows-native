#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 128MB -lt 20GB){throw 'Projected 20GiB reserve'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/demo-integration251/prepare-emulator.py
 if($LASTEXITCODE){throw 'Preparation failed; preserve unique attempt'}
}
