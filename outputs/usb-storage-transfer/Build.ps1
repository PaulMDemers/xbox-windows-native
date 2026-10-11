$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt (20GB+256MB)){throw 'Projected 20 GiB build guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 $linux=('/mnt/e'+$PSScriptRoot.Substring(2)).Replace('\','/')
 wsl -d Ubuntu -u root -- env XWN_BUILD_LEASE=held python3 -B "$linux/build.py"
 if($LASTEXITCODE){throw 'Private instrumented emulator build failed; preserve evidence'}
}
