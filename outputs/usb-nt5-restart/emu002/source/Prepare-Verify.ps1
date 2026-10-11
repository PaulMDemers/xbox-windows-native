$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
 $linux=('/mnt/e'+$PSScriptRoot.Substring(2)).Replace('\','/')
 wsl -d Ubuntu -- python3 -B "$linux/prepare-verify.py"
 if($LASTEXITCODE){throw 'Subsequent-boot preparation failed'}
}
