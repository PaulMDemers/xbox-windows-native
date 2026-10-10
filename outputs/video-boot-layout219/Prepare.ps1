#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB -or (Get-PSDrive E).Free -lt 20GB){throw '20GiB preparation guard'}
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/prepare-emulator.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 foreach($case in @('control001','candidate001')) {
  & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 $script $case
  if($LASTEXITCODE -ne 0){throw 'Preserve incomplete preparation; inspect records before any further action'}
 }
}
