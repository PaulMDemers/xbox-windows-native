#requires -Version 7.4
$ErrorActionPreference='Stop'
$k=$PSScriptRoot
$r=Get-Content "$k/runtime-prepared002.json" -Raw | ConvertFrom-Json
$root=$r.root
if(Test-Path "$k/launch002.json"){throw 'Consumed launch'}
if([DateTimeOffset]::UtcNow -ge [DateTimeOffset]::Parse('2026-10-18T13:50:00Z')){throw 'Closeout cutoff'}
if((Get-PSDrive C).Free-768MB -lt 20GB){throw 'Projected capacity guard'}
$pins=Get-Content "$k/emu-frozen003.json" -Raw | ConvertFrom-Json
foreach($v in $pins.PSObject.Properties){if((Get-FileHash -LiteralPath $v.Name).Hash.ToLowerInvariant() -ne $v.Value){throw ('Changed input: '+$v.Name)}}
$source=$r.emulator.source
if((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $r.emulator.sha256){throw 'Emulator changed'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 $p=$null;$fallback=$false;$deadlineHit=$false;$natural=$false
 try {
  @{utc=[DateTime]::UtcNow.ToString('o');physical_access=$false;fresh_unused_fixture=$true} | ConvertTo-Json | Set-Content "$k/launch002.json"
  $p=& "$k/start-instance.ps1" -TaskId dispatch527-emu002 -XemuPath $source -ConfigPath "$root/config.toml" -RunDirectory $root -InstanceRoot C:/xwn527/instances -ScratchRoot C:/xwn527/scratch -ArgumentList @('-dvd_path',"$root/utility.iso",'-no-reboot','-monitor','tcp:127.0.0.1:6277,server,nowait','-net','none')
  $deadline=[DateTime]::UtcNow.AddSeconds(90)
  while(-not $p.HasExited -and [DateTime]::UtcNow -lt $deadline){Start-Sleep -Seconds 1;$p.Refresh()}
  $natural=$p.HasExited
  if(-not $natural){
   $deadlineHit=$true
   $tcp=[Net.Sockets.TcpClient]::new();$task=$tcp.ConnectAsync('127.0.0.1',6277)
   if(-not $task.Wait(3000)){throw 'Monitor connection deadline'}
   try{$tcp.SendTimeout=3000;$b=[Text.Encoding]::ASCII.GetBytes("stop`nquit`n");$tcp.GetStream().Write($b,0,$b.Length)}finally{$tcp.Dispose()}
   if(-not $p.WaitForExit(10000)){throw 'Orderly quit timed out'}
  }
 } finally {
  if($p -and -not $p.HasExited){$fallback=$true;$p.Kill();if(-not $p.WaitForExit(10000)){throw 'Owned process still running'}}
  @{closed=$(-not $p -or $p.HasExited);pid=$(if($p){$p.Id}else{$null});fallback=$fallback;deadline_reached=$deadlineHit;natural_exit=$natural;exit=$(if($p){$p.ExitCode}else{$null});utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content "$k/closure002.json"
 }
}
