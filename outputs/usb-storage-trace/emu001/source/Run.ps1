param([Parameter(Mandatory)][ValidatePattern('^emu[0-9]{3}$')][string]$Case)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$canon='C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility'
$run="$repo/work/runs/nt5stortrace-$Case"
if(-not (Test-Path "$run/stage.json")){throw 'Prepare a fresh fixture first'}
if((Test-Path "$run/instance.json") -or (Test-Path "$run/cleanup.json")){throw 'Never relaunch an emulator attempt'}
if((Get-Content "$repo/.git/HEAD" -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-usb'){throw 'Wrong branch'}
if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
if(-not $env:XWN_EMULATOR_FTP_USER -or -not $env:XWN_EMULATOR_FTP_PASSWORD){throw 'Loopback credentials required in environment'}
if($env:XWN_NATIVE_EVENT_LOG -or $env:XWN_NV2A_RESOURCE_MODEL){throw 'Unexpected emulator experiment'}
$seed="$repo/outputs/usb-identification207/artifacts/emu001/seed.qcow2"
if((Get-FileHash $seed).Hash.ToLowerInvariant() -ne '7c09d05af676a7c37f242850837a8b2fa19b81a6ae63b2af2ec156e9a5fa197b'){throw 'Seed drift'}
$exe="$repo/work/runtime/xemu207/xemu-usb207.exe"
if((Get-FileHash $exe).Hash.ToLowerInvariant() -ne '685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'){throw 'Emulator drift'}
$monitor=5114;$ftp=5116
foreach($port in @($monitor,$ftp)){$s=[Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$port);try{$s.Start()}finally{$s.Stop()}}
try {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu-ui -Action {
   if((Test-Path "$run/instance.json") -or (Test-Path "$run/cleanup.json")){throw 'Attempt already used'}
   $stage=Get-Content "$run/stage.json" -Raw | ConvertFrom-Json
   if(-not $stage.baseline_exact -or -not $stage.allocation_passed){throw 'Unqualified fixture'}
   if((Get-FileHash "$run/hdd.qcow2").Hash.ToLowerInvariant() -ne $stage.staged_disk_sha256){throw 'Staged overlay drift'}
   Copy-Item "$canon/work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin" "$run/eeprom.bin"
   $bios='C:/Emulators/xemu/system/bios/Complex_4627.bin';$mcpx='C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin'
   $iso="$canon/outputs/native-windows-extended-storage/artifacts/f-boot-length-004.iso"
   @($exe,$seed,$bios,$mcpx,$iso,"$run/eeprom.bin") | Get-FileHash | ConvertTo-Json | Set-Content "$run/input-hashes.json"
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
   Copy-Item -LiteralPath "$PSScriptRoot/trace-events.txt" -Destination "$run/trace-events.txt"
   $arguments=@('-trace',"events=$run/trace-events.txt,file=$run/host-io.trace",'-config_path',"$run/config.toml",'-m','64','-dvd_path',$iso,'-machine','xbox,kernel-irqchip=off,avpack=composite','-monitor',"tcp:127.0.0.1:${monitor},server,nowait",'-nic',"user,id=nt5xidnet,model=nvnet,restrict=on,hostfwd=tcp:127.0.0.1:${ftp}-:21")
   $vm=$null
   try {
    $vm=Start-Process $exe -ArgumentList $arguments -WorkingDirectory $run -WindowStyle Hidden -PassThru -RedirectStandardOutput "$run/stdout.log" -RedirectStandardError "$run/stderr.log" -Environment @{TEMP=$run;TMP=$run;TMPDIR=$run}
    @{pid=$vm.Id;started_utc=[DateTime]::UtcNow.ToString('o');physical_access=$false;monitor_port=$monitor;ftp_port=$ftp;arguments=$arguments} | ConvertTo-Json -Depth 4 | Set-Content "$run/instance.json"
    $env:PYTHONPATH="$canon/work/python-packages"
    python -B "$PSScriptRoot/observe.py" $Case
    if($LASTEXITCODE){throw 'Observer failure retained'}
   } finally {
    $stopped=$false;if($vm){$vm.Refresh();if(-not $vm.HasExited){$vm.Kill();$vm.WaitForExit();$stopped=$true}}
    @{closed_utc=[DateTime]::UtcNow.ToString('o');host_stopped=$stopped;physical_access=$false} | ConvertTo-Json | Set-Content "$run/cleanup.json"
   }
  }
 }
} catch {
 @{case=$Case;error=$_.ToString();physical_access=$false;run_exists=(Test-Path $run)} | ConvertTo-Json | Set-Content "$PSScriptRoot/$Case-failure.json"
 throw
}
