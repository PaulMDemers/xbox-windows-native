#requires -Version 7.4
param([ValidatePattern('^emu[0-9]{3}$')][string]$Case='emu002')
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-Content "$repo/.git/HEAD" -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-usb'){throw 'Wrong branch'}
if((& git -C $repo config --get remote.origin.url).Trim() -ne 'https://github.com/PaulMDemers/xbox-windows-native.git'){throw 'Wrong origin'}
if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
if(-not $env:XWN_EMULATOR_FTP_USER -or -not $env:XWN_EMULATOR_FTP_PASSWORD){throw 'Loopback emulator credentials must be supplied in the process environment'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected emulator experiment environment'}
$canonical='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility'
$fixture=Get-Content "$PSScriptRoot/fixture-emu001.json" -Raw | ConvertFrom-Json
$seed="$PSScriptRoot/artifacts/emu001/seed.qcow2"
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne $fixture.seed_sha256){throw 'Seed changed'}
$exe="$canonical/outputs/xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe"
$hash='685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne $hash){throw 'Emulator changed'}
$run="$repo/work/runs/usb207-$Case"
$MonitorPort=4804+10*[int]$Case.Substring(3)
$FtpPort=$MonitorPort+2
if(Test-Path $run){throw 'Never reuse a run ID'}
foreach($port in @($MonitorPort,$FtpPort)){$s=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$port);try{$s.Start()}finally{$s.Stop()}}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu-ui -Action {
 New-Item -ItemType Directory $run -ErrorAction Stop | Out-Null
 $portable="$repo/work/runtime/xemu207"
 New-Item -ItemType Directory $portable -Force | Out-Null
 if(-not (Test-Path "$portable/xemu-usb207.exe")){Copy-Item $exe "$portable/xemu-usb207.exe"}
 if((Get-FileHash "$portable/xemu-usb207.exe").Hash.ToLowerInvariant() -ne $hash){throw 'Portable emulator changed'}
 "[general]`nshow_welcome = false`n[general.updates]`ncheck = false`n" | Set-Content "$portable/xemu.toml"
 $exe="$portable/xemu-usb207.exe"
 Copy-Item $seed "$run/hdd.qcow2"
 $eeprom="$canonical/work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin"
 Copy-Item $eeprom "$run/eeprom.bin"
 $bios='C:/Emulators/xemu/system/bios/Complex_4627.bin'
 $mcpx='C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'
 $iso="$canonical/outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso"
 @($exe,$seed,$eeprom,$bios,$mcpx,$iso) | Get-FileHash | ConvertTo-Json | Set-Content "$run/input-hashes.json"
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
bootrom_path = '$mcpx'
flashrom_path = '$bios'
eeprom_path = '$run/eeprom.bin'
hdd_path = '$run/hdd.qcow2'
[net]
enable = false
"@ | Set-Content "$run/config.toml"
 $arguments=@('-config_path',"$run/config.toml",'-no-shutdown','-no-reboot','-m','64','-dvd_path',$iso,'-machine','xbox,kernel-irqchip=off,avpack=composite','-device','usb-kbd,id=usb207kbd','-device','usb-mouse,id=usb207mouse','-monitor',"tcp:127.0.0.1:${MonitorPort},server,nowait",'-nic',"user,id=usb207net,model=nvnet,restrict=on,hostfwd=tcp:127.0.0.1:${FtpPort}-:21",'-d','cpu_reset,guest_errors','-D',"$run/cpu-trace.log")
 function Quote([string]$v){'"'+([regex]::Replace([regex]::Replace($v,'(\\*)"','$1$1\"'),'(\\+)$','$1$1'))+'"'}
 $vm=$null
 try{
  $vm=Start-Process -FilePath $exe -ArgumentList (($arguments | ForEach-Object {Quote $_}) -join ' ') -WorkingDirectory $run -WindowStyle Hidden -PassThru -RedirectStandardOutput "$run/stdout.log" -RedirectStandardError "$run/stderr.log" -Environment @{TEMP=$run;TMP=$run;TMPDIR=$run}
  @{pid=$vm.Id;started_utc=[DateTime]::UtcNow.ToString('o');emulator_sha256=$hash;run=$run;exclusive_xemu=$true;physical_access=$false;arguments=$arguments} | ConvertTo-Json -Depth 3 | Set-Content "$run/instance.json"
  Copy-Item "$PSScriptRoot/Run.ps1","$PSScriptRoot/observe.py" $run
  $env:PYTHONPATH="$canonical/work/python-packages"
  $env:USB207_MONITOR_PORT=[string]$MonitorPort
  $env:USB207_FTP_PORT=[string]$FtpPort
  & python -B "$PSScriptRoot/observe.py" $Case
  if($LASTEXITCODE){throw 'Observer failed; retain diagnostic attempt'}
 }finally{
  $stopped=$false;$exitCode=$null
  if($vm){$vm.Refresh();if(-not $vm.HasExited){$vm.Kill();$vm.WaitForExit();$stopped=$true};$exitCode=$vm.ExitCode}
  @{closed_utc=[DateTime]::UtcNow.ToString('o');host_stopped=$stopped;exit_code=$exitCode;normal_shutdown_qualified=$false;physical_access=$false} | ConvertTo-Json | Set-Content "$run/cleanup.json"
 }
 }
}
