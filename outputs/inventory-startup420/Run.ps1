$ErrorActionPreference='Stop'
$k=$PSScriptRoot
$r=Get-Content "$k/prepared001.json" -Raw | ConvertFrom-Json
$root=$r.root
if(Test-Path "$k/launch001.json"){throw 'Consumed launch'}
if((Get-PSDrive C).Free-64MB -lt 20GB -or (Get-PSDrive E).Free-64MB -lt 20GB){throw 'Projected capacity guard'}
$source=$r.emulator.source
$hash=(Get-FileHash -LiteralPath $source).Hash
if($hash.ToLowerInvariant() -ne $r.emulator.sha256){throw 'Emulator changed'}
# Same-volume hardlink to immutable closed executable saves a redundant 191MB copy.
# No byte writes to either executable; the launcher verifies its hash independently.
$instances='C:/Users/Paul/AppData/Local/ogxbox-linux/instances'
$portable=Join-Path $instances ('inventory-startup420/'+$hash.Substring(0,16))
if(Test-Path $portable){throw 'Consumed portable'}
New-Item -ItemType Directory -Path $portable | Out-Null
New-Item -ItemType HardLink -Path (Join-Path $portable 'xemu-inventory-startup420.exe') -Target $source | Out-Null
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Shared -Action {
 $p=$null;$fallback=$false
 try {
  @{utc=[DateTime]::UtcNow.ToString('o');physical_access=$false} | ConvertTo-Json | Set-Content "$k/launch001.json"
  $p=& C:/Users/Paul/Desktop/ogxbox-linux/scripts/start_xemu_instance.ps1 -TaskId inventory-startup420 -XemuPath $source -ConfigPath "$root/config.toml" -RunDirectory $root -InstanceRoot $instances -ScratchRoot E:/xwn420/scratch -ArgumentList @('-dvd_path',"$root/utility.iso",'-no-reboot','-monitor','tcp:127.0.0.1:5420,server,nowait','-net','none')
  Start-Sleep -Seconds 15
  if(-not $p.HasExited){
   $tcp=[Net.Sockets.TcpClient]::new('127.0.0.1',5420)
   $b=[Text.Encoding]::ASCII.GetBytes("screendump E:/xwn420/emu001/screen.ppm`n");$tcp.GetStream().Write($b,0,$b.Length);Start-Sleep -Milliseconds 500;$tcp.Dispose()
  }
  $deadline=[DateTime]::UtcNow.AddSeconds(90)
  while(-not $p.HasExited -and [DateTime]::UtcNow -lt $deadline){Start-Sleep -Seconds 1;$p.Refresh()}
  if(-not $p.HasExited){
   $tcp=[Net.Sockets.TcpClient]::new('127.0.0.1',5420)
   $b=[Text.Encoding]::ASCII.GetBytes("stop`nquit`n");$tcp.GetStream().Write($b,0,$b.Length);$tcp.Dispose()
   if(-not $p.WaitForExit(10000)){throw 'Orderly quit timed out'}
  }
 } finally {
  if($p -and -not $p.HasExited){$fallback=$true;$p.Kill();$p.WaitForExit()}
  @{closed=$true;fallback=$fallback;exit=$(if($p){$p.ExitCode}else{$null});utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content "$k/closure001.json"
 }
}
