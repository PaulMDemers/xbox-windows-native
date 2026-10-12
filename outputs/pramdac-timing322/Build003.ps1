#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free - 512MB -lt 20GB){throw 'Projected build reserve below20GiB'}
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/build003.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 -B $script
 if($LASTEXITCODE){throw 'Build failed; preserve unique attempt'}
}
