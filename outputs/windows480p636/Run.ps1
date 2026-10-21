#requires -Version 7.4
$ErrorActionPreference='Stop'
$k=$PSScriptRoot;$root='C:/xwn636/emu001'
$r=Get-Content (Join-Path $k runtime001.json) -Raw | ConvertFrom-Json
if(Test-Path (Join-Path $k runner001.json)){throw '636 runtime consumed'}
if((Get-PSDrive C).Free-192MB -lt 20GB){throw '636 projected reserve'}
foreach($group in @($r.dependencies,$r.parents,$r.initial)){foreach($p in $group.PSObject.Properties){if((Get-FileHash $p.Name).Hash.ToLowerInvariant() -ne $p.Value){throw ('Pin changed: '+$p.Name)}}}
if((Get-FileHash $r.emulator.private).Hash.ToLowerInvariant() -ne $r.emulator.sha256){throw 'Emulator pin'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 $vm=$null;$watch=$null;$fallback=$false
 try {
  @{utc=[DateTime]::UtcNow.ToString('o');physical_access=$false;debugger=$false;direct_optical_boot=$true;site_requests=0} | ConvertTo-Json | Set-Content (Join-Path $k runner001.json)
  $vm=& C:/Users/Paul/Desktop/ogxbox-linux/scripts/start_xemu_instance.ps1 -TaskId windows-native-480p636 -XemuPath $r.emulator.source -ConfigPath (Join-Path $root config.toml) -RunDirectory $root -InstanceRoot C:/xwn636/instances -ScratchRoot C:/xwn636/scratch -ArgumentList @('-no-reboot','-no-shutdown','-dvd_path',(Join-Path $root boot.iso),'-m','64','-machine','xbox,kernel-irqchip=off,avpack=hdtv','-device','usb-kbd','-device','usb-mouse','-net','none','-monitor','tcp:127.0.0.1:5668,server,nowait','-d','cpu_reset,guest_errors','-D',(Join-Path $root cpu.log))
  $watch=Start-Process C:/Python314/python.exe -ArgumentList @('-B',('"'+(Join-Path $k observe.py)+'"')) -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $root observer.stdout.log) -RedirectStandardError (Join-Path $root observer.stderr.log)
  if(-not $watch.WaitForExit(630000)){throw '636 observer deadline'}
  if(-not $vm.WaitForExit(15000)){throw '636 host quit timeout'}
 } finally {
  if($watch -and -not $watch.HasExited){$watch.Kill();$watch.WaitForExit()}
  if($vm -and -not $vm.HasExited){$fallback=$true;$vm.Kill();$vm.WaitForExit()}
  @{closed=$true;utc=[DateTime]::UtcNow.ToString('o');fallback_kill=$fallback;host_exit=$(if($vm){$vm.ExitCode}else{$null});observer_exit=$(if($watch){$watch.ExitCode}else{$null})} | ConvertTo-Json | Set-Content (Join-Path $k closure001.json)
 }
}
