#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20GiB guard unchanged'}
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/prepare.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 $script
    if($LASTEXITCODE){throw 'Preserve260 fixture failure; never reuse attempt'}
}
