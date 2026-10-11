#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB){throw '20GiB guard unchanged'}
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/build-renderer001.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 $script
    if($LASTEXITCODE){throw 'Preserve259 renderer-build001 failure; no reuse'}
}
