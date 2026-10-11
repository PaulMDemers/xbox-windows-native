param([ValidateSet('stage','audit')][string]$Mode,[ValidateSet('emu001','emu002')][string]$Case)
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
 $linux=('/mnt/e'+$PSScriptRoot.Substring(2)).Replace('\','/')
 wsl -d Ubuntu -- python3 -B "$linux/disk.py" $Mode $Case
 if($LASTEXITCODE){throw 'Disk operation failed'}
 if($Mode -eq 'audit'){
  foreach($script in @('audit-details.py','typed-state.py','no-xid-state.py')){
   wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 -B "$linux/$script" $Case
   if($LASTEXITCODE){throw "Cold audit failed: $script"}
  }
 }
}
