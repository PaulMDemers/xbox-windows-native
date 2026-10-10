#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20GiB build guard'}
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/build.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 $script
 if($LASTEXITCODE -ne 0){throw 'Preserve staging build failure; never reuse build001'}
}
