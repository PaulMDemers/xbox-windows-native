#requires -Version 7.4
$ErrorActionPreference='Stop'
for($attempt=0;$attempt -lt 45;$attempt++){
 try {
  & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
   & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207/hidreject007/extract-providers001.py
   if($LASTEXITCODE){throw 'Provider extraction failed; retain partial attempt'}
  }
  exit 0
 } catch {
  if($_.Exception.Message -notlike "Xbox resource '*' is busy or unavailable*"){throw}
 }
 Start-Sleep -Seconds 20
}
throw 'Bounded build-lease wait expired; no bypass'
