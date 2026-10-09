#requires -Version 7.4
$ErrorActionPreference='Stop'
if ((Get-PSDrive C).Free -lt 20GB) { throw '20GiB guard' }
$script=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/build.py'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 $script /home/paul/xbox-windows-native/build/video-text-bounds203-001
 if ($LASTEXITCODE -ne 0) { throw 'Fresh RAM-primary display build failed; preserve report' }
}
