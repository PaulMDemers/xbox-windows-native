#requires -Version 7.4
param([ValidateSet('trace001')][string]$Case)
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB -or (Get-PSDrive E).Free -lt 20GB){throw '20GiB preparation guard'}
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/prepare.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 $script $Case
 if($LASTEXITCODE -ne 0){throw 'Preserve failed preparation; never reuse attempt IDs'}
}
