#requires -Version 7.4
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-z0-9-]+$')][string]$RunId,
    [ValidatePattern('^windows-native(-[a-z0-9-]+)?$')][string]$InstanceTask = 'windows-native',
    [Parameter(Mandatory)][string]$Bios,
    [Parameter(Mandatory)][string]$Iso,
    [string]$HddSource,
    [string]$EepromSource,
    [string]$EmulatorPath = 'C:\Users\Paul\Desktop\ogxbox-linux\tools\xemu-nvnet-fresh\xemu.exe',
    [ValidatePattern('^[a-fA-F0-9]{64}$')][string]$EmulatorSha256 = '392C3FEE86E47A5452A32ED31E280B62D2074C260A2C1195441ED5DDCC0A3D55',
    [ValidateRange(0,65535)][int]$FtpPort = 0,
    [switch]$LaunchXromwell,
    [switch]$UsbMouse,
    [switch]$ExerciseInput,
    [switch]$Autorun,
    [switch]$RetainDisk,
    [switch]$AllowGuestReboot,
    [switch]$InstallNetwork,
    [switch]$TraceNetwork,
    [switch]$TracePackets,
    [switch]$TraceDiskWrites,
    [switch]$CompactTrace,
    [switch]$CaptureAudio,
    [switch]$ManualCapture,
    [switch]$StopOnCaptureComplete,
    [switch]$StopOnBugcheck,
    [switch]$AllowFramebufferFallback,
    [ValidateRange(1,1920)][int]$CaptureWidth = 640,
    [ValidateRange(1,1080)][int]$CaptureHeight = 480,
    [ValidateRange(4,8192)][int]$CapturePitch = 2560,
    [ValidateRange(1024,65535)][int]$MonitorPort = 4574,
    [ValidateRange(1024,65535)][int]$GdbPort = 4575,
    [ValidateRange(30,3600)][int]$Seconds = 120
)
$ErrorActionPreference = 'Stop'
$DiagnosticRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../native-windows-nt5-kernel'))
if ($CapturePitch -lt $CaptureWidth * 4 -or $CapturePitch % 4 -ne 0 -or $CapturePitch * $CaptureHeight -gt 4MB) {
    throw 'Capture geometry must describe a 32-bit framebuffer within four MiB.'
}
if ($ManualCapture -and ($Autorun -or $LaunchXromwell -or $ExerciseInput -or $InstallNetwork -or $TraceNetwork)) {
    throw 'Manual capture requires explicit external launch/inspection; automatic actions cannot be combined with it.'
}
if ($TracePackets -and -not $FtpPort) { throw 'Packet tracing needs the private network backend.' }
if ($LaunchXromwell -and -not $FtpPort) { throw 'LaunchXromwell needs the private FTP forward.' }
$workspace = Split-Path -Parent (Split-Path -Parent $DiagnosticRoot)
if ($workspace -ne [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))) { throw 'Workspace root mismatch' }
$run = Join-Path "E:/Codex-private-artifacts/xbox-windows-feasibility/guest236-runs" $RunId
$captureComplete = Join-Path $run 'capture-complete.signal'
if (Test-Path -LiteralPath $run) { throw 'Choose an unused run id.' }
$integration = 'C:\Users\Paul\Desktop\ogxbox-linux\scripts'
$xemu = (Resolve-Path -LiteralPath $EmulatorPath).Path
$mcpx = 'C:\Emulators\xemu\system\mcpx\mcpx_1.0.bin'
$blank = 'C:\Emulators\xemu\system\xbox_hdd.qcow2'
if ($HddSource) { $blank = (Resolve-Path -LiteralPath $HddSource).Path }
$originalEeprom = 'C:\Emulators\xemu\eeprom.bin'
if ($EepromSource) { $originalEeprom = (Resolve-Path -LiteralPath $EepromSource).Path }
$biosPath = (Resolve-Path -LiteralPath $Bios).Path
$isoPath = (Resolve-Path -LiteralPath $Iso).Path
if ((Get-FileHash $xemu).Hash -ne $EmulatorSha256) { throw 'Unexpected emulator binary.' }
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
& {
    $vm = $null
    try {
        $vmArguments = @('-no-reboot','-no-shutdown','-gdb',"tcp:127.0.0.1:$GdbPort",'-d','cpu_reset,int,guest_errors','-D',(Join-Path $run cpu-trace.log),'-m','64','-snapshot','-dvd_path',$isoPath,'-machine','xbox,kernel-irqchip=off,avpack=composite','-device','usb-kbd','-monitor',"tcp:127.0.0.1:$MonitorPort,server,nowait")
        if ($CompactTrace) { $vmArguments = @($vmArguments | ForEach-Object { if ($_ -eq 'cpu_reset,int,guest_errors') { 'cpu_reset,guest_errors' } else { $_ } }) }
        # Sparse lifecycle events start before guest firmware; CPU access events stay off.
        foreach ($eventName in @('create_color','create_zeta','invalidated','evict_reason','evict_overlapping','upload','download')) {
            $vmArguments += @('-trace',('enable=nv2a_pgraph_surface_'+$eventName))
        }
        if ($UsbMouse) { $vmArguments += @('-device','usb-mouse') }
        if ($RetainDisk) { $vmArguments = @($vmArguments | Where-Object { $_ -ne '-snapshot' }) }
        if ($AllowGuestReboot) { $vmArguments = @($vmArguments | Where-Object { $_ -ne '-no-reboot' }) }
        if ($TraceDiskWrites) { $vmArguments += @('-trace','enable=ide_sector_write','-trace','enable=blk_co_pwritev') }
        if ($FtpPort) { $vmArguments += @('-nic',"user,id=xemu-netdev,model=nvnet,restrict=on,hostfwd=tcp:127.0.0.1:${FtpPort}-:21") }
        if ($TracePackets) { $vmArguments += @('-object',"filter-dump,id=xwn-pcap,netdev=xemu-netdev,file=$(Join-Path $run 'nvnet.pcap')") }
        $vm = & (Join-Path $integration 'start_xemu_instance.ps1') -TaskId $InstanceTask -XemuPath $xemu -ConfigPath $config -RunDirectory $run -ScratchRoot 'E:/Codex-private-artifacts/xbox-windows-feasibility/guest236-scratch' -ArgumentList $vmArguments
        if ($CaptureAudio) {
            $captureFile = (Join-Path $run 'ac97-output.wav').Replace('\','/')
            & python (Join-Path (Join-Path $DiagnosticRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --command "wavcapture `"$captureFile`" `"#default`" 48000 16 2"
            if ($LASTEXITCODE -ne 0) { throw 'Could not start private audio capture.' }
        }
        if ($FtpPort) {
            & python (Join-Path (Join-Path $DiagnosticRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --command 'set_link nvnet.0 on'
            if ($LASTEXITCODE -ne 0) { throw 'Could not enable the private guest link.' }
        }
        @{utc=[DateTime]::UtcNow.ToString('o');nic_ready=$true;monitor_ready=$true} | ConvertTo-Json | Set-Content (Join-Path $run 'startup-ready.json')
        $clock = [Diagnostics.Stopwatch]::StartNew()
        $nextCapture = 15
        $launchSent = $false
        $inputSent = $false
        $networkInstallSent = $false
        while ($clock.Elapsed.TotalSeconds -lt $Seconds) {
            $traceFile=Join-Path $run 'cpu-trace.log'
            if ((Test-Path -LiteralPath $traceFile) -and (Get-Item -LiteralPath $traceFile).Length -gt 16MB) { throw 'Lifecycle trace exceeded 16 MiB bound' }
            $vm.Refresh()
            if ($vm.HasExited) { throw "Task emulator exited: $($vm.ExitCode)" }
            if (-not $ManualCapture -and $clock.Elapsed.TotalSeconds -ge $nextCapture) {
                $output = Join-Path $run ('frame-{0:D3}.png' -f $nextCapture)
                $captureArguments = @('--port',$MonitorPort,'--output',$output,'--width',$CaptureWidth,'--height',$CaptureHeight,'--pitch',$CapturePitch)
                if ($FtpPort) { $captureArguments += '--auto-framebuffer' }
                if ($AllowFramebufferFallback) { $captureArguments += '--fallback-framebuffer' }
                & python (Join-Path (Join-Path $DiagnosticRoot ../native-windows-prebuild) 'monitor_capture.py') @captureArguments
                if ($LASTEXITCODE -ne 0) { throw 'Guest capture failed.' }
                $captureScript = if ($Autorun) { 'capture-runtime.py' } else { 'capture-state.py' }
                & C:/Python314/python.exe (Join-Path $DiagnosticRoot $captureScript) --port $MonitorPort --output (Join-Path $run ('state-{0:D3}.json' -f $nextCapture))
                if ($LASTEXITCODE -ne 0) { throw 'Guest state inspection failed.' }
                $statePath = Join-Path $run ('state-{0:D3}.json' -f $nextCapture)
                $state = Get-Content -Raw $statePath | ConvertFrom-Json
                if ($Autorun -and $state.status -eq 'shell_running' -and $InstallNetwork -and -not $networkInstallSent -and $nextCapture -ge 60) {
                    & C:/Python314/python.exe (Join-Path $DiagnosticRoot 'launch-network-install.py') --port $MonitorPort --run $run
                    if ($LASTEXITCODE -ne 0) { throw 'Network installer launch failed.' }
                    $networkInstallSent = $true
                }
                if ($Autorun -and $state.status -eq 'shell_running' -and $ExerciseInput -and -not $inputSent -and $nextCapture -ge 60) {
                    & C:/Python314/python.exe (Join-Path $DiagnosticRoot 'exercise-input.py') --port $MonitorPort --run $run --width $CaptureWidth --height $CaptureHeight --pitch $CapturePitch
                    if ($LASTEXITCODE -ne 0) { throw 'Input exercise failed.' }
                    $inputSent = $true
                }
                if ($StopOnBugcheck -and $state.status -eq 'bugcheck_reported') {
                    @{reason='guest_bugcheck'; run=$RunId; state=$statePath; bugcheck=$state.bugcheck_data} | ConvertTo-Json | Set-Content (Join-Path $run 'completion.json')
                    break
                }
                if ($state.status -eq 'pre_entry_halt_verified') {
                    $traceOptions = @()
                    if ($TraceNetwork) { $traceOptions += '--trace-network' }
                    & C:/Python314/python.exe (Join-Path $DiagnosticRoot 'trace-entry.py') @traceOptions --port $GdbPort --monitor $MonitorPort --state $statePath --output (Join-Path $run 'kernel-trace.json')
                    if ($LASTEXITCODE -ne 0) { throw 'Kernel trace helper failed.' }
                    & python (Join-Path (Join-Path $DiagnosticRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --output (Join-Path $run 'after-kernel.png') --width $CaptureWidth --height $CaptureHeight --pitch $CapturePitch
                    if ($ExerciseInput) {
                        & C:/Python314/python.exe (Join-Path $DiagnosticRoot 'exercise-input.py') --port $MonitorPort --run $run --width $CaptureWidth --height $CaptureHeight --pitch $CapturePitch
                        if ($LASTEXITCODE -ne 0) { throw 'Input exercise failed.' }
                    }
                    break
                }
                if ($LaunchXromwell -and -not $launchSent -and $nextCapture -ge 30) {
                    if ($TraceDiskWrites) {
                        @{
                            recordedUtc = [DateTime]::UtcNow.ToString('o')
                            traceBytesBeforeLaunch = (Get-Item -LiteralPath (Join-Path $run cpu-trace.log)).Length
                        } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $run disk-trace-prelaunch.json)
                    }
                    & python (Join-Path (Join-Path $DiagnosticRoot ../native-windows-prebuild) 'launch_unleashx.py') --port $FtpPort --output (Join-Path $run 'launch-command.json')
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
            & python (Join-Path (Join-Path $DiagnosticRoot ../native-windows-prebuild) 'monitor_capture.py') --port $MonitorPort --command 'stopcapture 0'
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
