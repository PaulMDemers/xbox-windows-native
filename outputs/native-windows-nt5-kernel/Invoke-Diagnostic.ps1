#requires -Version 7.4
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-z0-9-]+$')][string]$RunId,
    [ValidatePattern('^windows-native(-[a-z0-9-]+)?$')][string]$InstanceTask = 'windows-native',
    [Parameter(Mandatory)][string]$Bios,
    [Parameter(Mandatory)][string]$Iso,
    [string]$HddSource,
    [string]$EepromSource,
    [ValidateRange(0,65535)][int]$FtpPort = 0,
    [switch]$LaunchXromwell,
    [switch]$UsbMouse,
    [switch]$ExerciseInput,
    [switch]$Autorun,
    [switch]$RetainDisk,
    [switch]$InstallNetwork,
    [switch]$TraceNetwork,
    [switch]$TracePackets,
    [switch]$CaptureAudio,
    [switch]$ManualCapture,
    [switch]$StopOnCaptureComplete,
    [ValidateRange(1024,65535)][int]$MonitorPort = 4574,
    [ValidateRange(1024,65535)][int]$GdbPort = 4575,
    [ValidateRange(30,3600)][int]$Seconds = 120
)
$ErrorActionPreference = 'Stop'
if ($ManualCapture -and ($Autorun -or $LaunchXromwell -or $ExerciseInput -or $InstallNetwork -or $TraceNetwork)) {
    throw 'Manual capture requires explicit external launch/inspection; automatic actions cannot be combined with it.'
}
if ($StopOnCaptureComplete -and -not $ManualCapture) { throw 'Capture completion signal requires manual capture.' }
if ($TracePackets -and -not $FtpPort) { throw 'Packet tracing needs the private network backend.' }
if ($LaunchXromwell -and -not $FtpPort) { throw 'LaunchXromwell needs the private FTP forward.' }
$workspace = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$run = Join-Path $workspace "work\runs\$RunId"
$captureComplete = Join-Path $run 'capture-complete.signal'
if (Test-Path -LiteralPath $run) { throw 'Choose an unused run id.' }
$integration = 'C:\Users\Paul\Desktop\ogxbox-linux\scripts'
$xemu = 'C:\Users\Paul\Desktop\ogxbox-linux\tools\xemu-nvnet-fresh\xemu.exe'
$mcpx = 'C:\Emulators\xemu\system\mcpx\mcpx_1.0.bin'
$blank = 'C:\Emulators\xemu\system\xbox_hdd.qcow2'
if ($HddSource) { $blank = (Resolve-Path -LiteralPath $HddSource).Path }
$originalEeprom = 'C:\Emulators\xemu\eeprom.bin'
if ($EepromSource) { $originalEeprom = (Resolve-Path -LiteralPath $EepromSource).Path }
$biosPath = (Resolve-Path -LiteralPath $Bios).Path
$isoPath = (Resolve-Path -LiteralPath $Iso).Path
if ((Get-FileHash $xemu).Hash -ne '392C3FEE86E47A5452A32ED31E280B62D2074C260A2C1195441ED5DDCC0A3D55') { throw 'Unexpected emulator binary.' }
$probe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$MonitorPort)
try { $probe.Start() } finally { $probe.Stop() }
if ($GdbPort -eq $MonitorPort) { throw 'GDB and monitor ports must differ.' }
$probe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$GdbPort)
try { $probe.Start() } finally { $probe.Stop() }
if ($FtpPort) {
    if ($FtpPort -lt 1024 -or $FtpPort -eq $MonitorPort) { throw 'Use a distinct unprivileged FTP port.' }
    $probe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$FtpPort)
    try { $probe.Start() } finally { $probe.Stop() }
}
New-Item -ItemType Directory -Path $run | Out-Null
Copy-Item -LiteralPath $blank -Destination (Join-Path $run 'hdd.qcow2')
Copy-Item -LiteralPath $originalEeprom -Destination (Join-Path $run 'eeprom.bin')
$config = Join-Path $run 'config.toml'
@"
[general]
show_welcome = false
[general.updates]
check = false
[sys]
mem_limit = '64'
[sys.files]
bootrom_path = '$mcpx'
flashrom_path = '$biosPath'
eeprom_path = '$(Join-Path $run 'eeprom.bin')'
hdd_path = '$(Join-Path $run 'hdd.qcow2')'
[net]
enable = false
"@ | Set-Content -LiteralPath $config -Encoding utf8
@($biosPath,$isoPath,$mcpx,$blank,$originalEeprom) | Get-FileHash | ConvertTo-Json | Set-Content (Join-Path $run 'input-hashes.json')
& (Join-Path $integration 'with_xbox_resource.ps1') -Resource xemu -Shared -Action {
    $vm = $null
    try {
        $vmArguments = @('-no-reboot','-no-shutdown','-gdb',"tcp:127.0.0.1:$GdbPort",'-d','cpu_reset,int,guest_errors','-D',(Join-Path $run cpu-trace.log),'-m','64','-snapshot','-dvd_path',$isoPath,'-machine','xbox,kernel-irqchip=off,avpack=composite','-device','usb-kbd','-monitor',"tcp:127.0.0.1:$MonitorPort,server,nowait")
        if ($UsbMouse) { $vmArguments += @('-device','usb-mouse') }
        if ($RetainDisk) { $vmArguments = @($vmArguments | Where-Object { $_ -ne '-snapshot' }) }
        if ($FtpPort) { $vmArguments += @('-nic',"user,id=xemu-netdev,model=nvnet,restrict=on,hostfwd=tcp:127.0.0.1:${FtpPort}-:21") }
        if ($TracePackets) { $vmArguments += @('-object',"filter-dump,id=xwn-pcap,netdev=xemu-netdev,file=$(Join-Path $run 'nvnet.pcap')") }
        $vm = & (Join-Path $integration 'start_xemu_instance.ps1') -TaskId $InstanceTask -XemuPath $xemu -ConfigPath $config -RunDirectory $run -ScratchRoot (Join-Path $workspace 'work\scratch') -ArgumentList $vmArguments
        if ($CaptureAudio) {
            $captureFile = (Join-Path $run 'ac97-output.wav').Replace('\','/')
            & python (Join-Path (Join-Path $PSScriptRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --command "wavcapture `"$captureFile`" `"#default`" 48000 16 2"
            if ($LASTEXITCODE -ne 0) { throw 'Could not start private audio capture.' }
        }
        if ($FtpPort) {
            & python (Join-Path (Join-Path $PSScriptRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --command 'set_link nvnet.0 on'
            if ($LASTEXITCODE -ne 0) { throw 'Could not enable the private guest link.' }
        }
        $clock = [Diagnostics.Stopwatch]::StartNew()
        $nextCapture = 15
        $launchSent = $false
        $inputSent = $false
        $networkInstallSent = $false
        while ($clock.Elapsed.TotalSeconds -lt $Seconds) {
            $vm.Refresh()
            if ($vm.HasExited) { throw "Task emulator exited: $($vm.ExitCode)" }
            if (-not $ManualCapture -and $clock.Elapsed.TotalSeconds -ge $nextCapture) {
                $output = Join-Path $run ('frame-{0:D3}.png' -f $nextCapture)
                $captureArguments = @('--port',$MonitorPort,'--output',$output)
                if ($FtpPort) { $captureArguments += '--auto-framebuffer' }
                & python (Join-Path (Join-Path $PSScriptRoot ../native-windows-prebuild) 'monitor_capture.py') @captureArguments
                if ($LASTEXITCODE -ne 0) { throw 'Guest capture failed.' }
                $captureScript = if ($Autorun) { 'capture-runtime.py' } else { 'capture-state.py' }
                & C:/Python314/python.exe (Join-Path $PSScriptRoot $captureScript) --port $MonitorPort --output (Join-Path $run ('state-{0:D3}.json' -f $nextCapture))
                if ($LASTEXITCODE -ne 0) { throw 'Guest state inspection failed.' }
                $statePath = Join-Path $run ('state-{0:D3}.json' -f $nextCapture)
                $state = Get-Content -Raw $statePath | ConvertFrom-Json
                if ($Autorun -and $state.status -eq 'shell_running' -and $InstallNetwork -and -not $networkInstallSent -and $nextCapture -ge 60) {
                    & C:/Python314/python.exe (Join-Path $PSScriptRoot 'launch-network-install.py') --port $MonitorPort --run $run
                    if ($LASTEXITCODE -ne 0) { throw 'Network installer launch failed.' }
                    $networkInstallSent = $true
                }
                if ($Autorun -and $state.status -eq 'shell_running' -and $ExerciseInput -and -not $inputSent -and $nextCapture -ge 60) {
                    & C:/Python314/python.exe (Join-Path $PSScriptRoot 'exercise-input.py') --port $MonitorPort --run $run
                    if ($LASTEXITCODE -ne 0) { throw 'Input exercise failed.' }
                    $inputSent = $true
                }
                if ($state.status -eq 'pre_entry_halt_verified') {
                    $traceOptions = @()
                    if ($TraceNetwork) { $traceOptions += '--trace-network' }
                    & C:/Python314/python.exe (Join-Path $PSScriptRoot 'trace-entry.py') @traceOptions --port $GdbPort --monitor $MonitorPort --state $statePath --output (Join-Path $run 'kernel-trace.json')
                    if ($LASTEXITCODE -ne 0) { throw 'Kernel trace helper failed.' }
                    & python (Join-Path (Join-Path $PSScriptRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --output (Join-Path $run 'after-kernel.png')
                    if ($ExerciseInput) {
                        & C:/Python314/python.exe (Join-Path $PSScriptRoot 'exercise-input.py') --port $MonitorPort --run $run
                        if ($LASTEXITCODE -ne 0) { throw 'Input exercise failed.' }
                    }
                    break
                }
                if ($LaunchXromwell -and -not $launchSent -and $nextCapture -ge 30) {
                    & python (Join-Path (Join-Path $PSScriptRoot ../native-windows-prebuild) 'launch_unleashx.py') --port $FtpPort --output (Join-Path $run 'launch-command.json')
                    if ($LASTEXITCODE -ne 0) { throw 'UnleashX launch command failed.' }
                    $launchSent = $true
                }
                $nextCapture += 15
            }
            if ($StopOnCaptureComplete -and (Test-Path -LiteralPath $captureComplete -PathType Leaf)) {
                @{reason='external_capture_complete'; run=$RunId} | ConvertTo-Json | Set-Content (Join-Path $run 'completion.json')
                break
            }
            Start-Sleep -Milliseconds 250
        }
    } finally {
        if ($CaptureAudio -and $vm -and -not $vm.HasExited) {
            & python (Join-Path (Join-Path $PSScriptRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --command 'stopcapture 0'
        }
        if ($vm) { $vm.Refresh(); if (-not $vm.HasExited) { $vm.Kill(); $vm.WaitForExit() } }
        if (Test-Path (Join-Path $run 'instance.json')) {
            & (Join-Path $integration 'complete_xemu_instance.ps1') -RunDirectory $run
        }
        $ownedDisk = [IO.Path]::GetFullPath((Join-Path $run 'hdd.qcow2'))
        if ([IO.Path]::GetDirectoryName($ownedDisk) -ne [IO.Path]::GetFullPath($run)) { throw 'Unexpected staging disk path.' }
        if ($RetainDisk) {
            @{retained=$true; reason='Explicit private installation experiment; input disk preserved.'; path=$ownedDisk} | ConvertTo-Json | Set-Content (Join-Path $run 'disk-retention.json')
        } else {
            Remove-Item -LiteralPath $ownedDisk -ErrorAction SilentlyContinue
            @{retained=$false; reason='Read-only staging copy; guest used snapshot mode.'} | ConvertTo-Json | Set-Content (Join-Path $run 'disk-retention.json')
        }
    }
}
