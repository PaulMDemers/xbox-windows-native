param([ValidatePattern('^emu[0-9]{3}$')][string]$Case='emu001')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$canonical='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility'
$run="$repo/work/runs/xid-$Case"
if(Test-Path $run){throw 'Never reuse a run'}
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB C guard'}
if(-not $env:XWN_EMULATOR_FTP_USER -or -not $env:XWN_EMULATOR_FTP_PASSWORD){throw 'Credentials required in environment'}
$seed="$repo/outputs/usb-identification207/artifacts/emu001/seed.qcow2"
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne '7c09d05af676a7c37f242850837a8b2fa19b81a6ae63b2af2ec156e9a5fa197b'){throw 'Seed drift'}
$exe="$repo/work/runtime/xemu207/xemu-usb207.exe"
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne '685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'){throw 'Emulator drift'}
$env:XID_MONITOR_PORT='4964';$env:XID_FTP_PORT='4966'
foreach($port in @(4964,4966)){$s=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$port);try{$s.Start()}finally{$s.Stop()}}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu-ui -Action {
 New-Item -ItemType Directory $run | Out-Null
 $linuxRun=('/mnt/e'+$run.Substring(2)).Replace('\','/')
 & wsl -d Ubuntu --cd $linuxRun -- qemu-img create -f qcow2 -F qcow2 -b ../../../outputs/usb-identification207/artifacts/emu001/seed.qcow2 hdd.qcow2
 if($LASTEXITCODE){throw 'Overlay creation failed'}
 $linuxScript=('/mnt/e'+$PSScriptRoot.Substring(2)).Replace('\','/')+'/emulator-disk.py'
 & wsl -d Ubuntu -- env PYTHONDONTWRITEBYTECODE=1 python3 $linuxScript stage $Case
 if($LASTEXITCODE){throw 'E-only staging failed'}
 Copy-Item "$canonical/work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin" "$run/eeprom.bin"
 @"
[general]
show_welcome = false
[general.updates]
check = false
[input]
auto_bind = false
[input.bindings]
port1 = 'keyboard'
port1_driver = 'usb-xbox-gamepad'
[sys]
mem_limit = '64'
[sys.files]
bootrom_path = 'C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'
flashrom_path = 'C:/Emulators/xemu/system/bios/Complex_4627.bin'
eeprom_path = '$run/eeprom.bin'
hdd_path = '$run/hdd.qcow2'
[net]
enable = false
"@ | Set-Content "$run/config.toml"
 $arguments=@('-config_path',"$run/config.toml",'-m','64','-machine','xbox,kernel-irqchip=off,avpack=composite','-monitor','tcp:127.0.0.1:4964,server,nowait','-nic','user,id=xidnet,model=nvnet,restrict=on,hostfwd=tcp:127.0.0.1:4966-:21')
 $vm=$null
 try{
  $vm=Start-Process $exe -ArgumentList $arguments -WorkingDirectory $run -WindowStyle Hidden -PassThru -RedirectStandardOutput "$run/stdout.log" -RedirectStandardError "$run/stderr.log" -Environment @{TEMP=$run;TMP=$run;TMPDIR=$run}
  @{pid=$vm.Id;started_utc=[DateTime]::UtcNow.ToString('o');physical_access=$false;arguments=$arguments} | ConvertTo-Json -Depth 4 | Set-Content "$run/instance.json"
  python -B "$PSScriptRoot/observe-emulator.py" $Case
  if($LASTEXITCODE){throw 'Observer failed; evidence preserved'}
 }finally{
  $stopped=$false;if($vm){$vm.Refresh();if(-not $vm.HasExited){$vm.Kill();$vm.WaitForExit();$stopped=$true}}
  @{closed_utc=[DateTime]::UtcNow.ToString('o');host_stopped=$stopped;physical_access=$false} | ConvertTo-Json | Set-Content "$run/cleanup.json"
 }
 }
}
