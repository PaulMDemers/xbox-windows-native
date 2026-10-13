$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/hd-large-runtime330/prepare.py
 if($LASTEXITCODE){throw 'New330 preparation failed; preserve attempt'}
}
