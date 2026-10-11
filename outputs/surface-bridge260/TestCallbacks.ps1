#requires -Version 7.4
$ErrorActionPreference='Stop'
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/test-callbacks.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 $script
    if($LASTEXITCODE){throw 'Preserve260 callback-test failure; no repeat'}
}
