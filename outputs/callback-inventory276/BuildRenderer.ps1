#requires -Version 7.4
param([ValidateSet('003')][string]$Attempt='003')
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20GiB guard unchanged'}
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/build-renderer.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 $script $Attempt
    if($LASTEXITCODE){throw 'Preserve276 build failure; use fresh attempt for repairs'}
}
