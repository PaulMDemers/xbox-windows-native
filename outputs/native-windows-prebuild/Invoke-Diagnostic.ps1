#requires -Version 7.4
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-z0-9-]+$')][string]$RunId,
    [Parameter(Mandatory)][string]$Bios,
    [Parameter(Mandatory)][string]$Iso,
    [string]$HddSource,
    [ValidateRange(0,65535)][int]$FtpPort = 0,
    [switch]$LaunchXromwell,
    [ValidateRange(1024,65535)][int]$MonitorPort = 4574,
    [ValidateRange(30,300)][int]$Seconds = 120
)
$ErrorActionPreference = 'Stop'
if ($LaunchXromwell -and -not $FtpPort) { throw 'LaunchXromwell needs the private FTP forward.' }
$workspace = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$run = Join-Path $workspace "work\runs\$RunId"
if (Test-Path -LiteralPath $run) { throw 'Choose an unused run id.' }
$integration = 'C:\Users\Paul\Desktop\ogxbox-linux\scripts'
$xemu = 'C:\Users\Paul\Desktop\ogxbox-linux\tools\xemu-nvnet-fresh\xemu.exe'
$mcpx = 'C:\Emulators\xemu\system\mcpx\mcpx_1.0.bin'
$blank = 'C:\Emulators\xemu\system\xbox_hdd.qcow2'
if ($HddSource) { $blank = (Resolve-Path -LiteralPath $HddSource).Path }
$originalEeprom = 'C:\Emulators\xemu\eeprom.bin'
$biosPath = (Resolve-Path -LiteralPath $Bios).Path
$isoPath = (Resolve-Path -LiteralPath $Iso).Path
if ((Get-FileHash $xemu).Hash -ne '392C3FEE86E47A5452A32ED31E280B62D2074C260A2C1195441ED5DDCC0A3D55') { throw 'Unexpected emulator binary.' }
$probe = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback,$MonitorPort)
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
        $vmArguments = @('-m','64','-snapshot','-dvd_path',$isoPath,'-machine','xbox,kernel-irqchip=off,avpack=composite','-device','usb-kbd','-monitor',"tcp:127.0.0.1:$MonitorPort,server,nowait")
        if ($FtpPort) { $vmArguments += @('-nic',"user,id=xemu-netdev,model=nvnet,restrict=on,hostfwd=tcp:127.0.0.1:${FtpPort}-:21") }
        $vm = & (Join-Path $integration 'start_xemu_instance.ps1') -TaskId windows-native -XemuPath $xemu -ConfigPath $config -RunDirectory $run -ScratchRoot (Join-Path $workspace 'work\scratch') -ArgumentList $vmArguments
        if ($FtpPort) {
            & python (Join-Path $PSScriptRoot 'monitor_capture.py') --port $MonitorPort --command 'set_link nvnet.0 on'
            if ($LASTEXITCODE -ne 0) { throw 'Could not enable the private guest link.' }
        }
        $clock = [Diagnostics.Stopwatch]::StartNew()
        $nextCapture = 15
        $launchSent = $false
        while ($clock.Elapsed.TotalSeconds -lt $Seconds) {
            $vm.Refresh()
            if ($vm.HasExited) { throw "Task emulator exited: $($vm.ExitCode)" }
            if ($clock.Elapsed.TotalSeconds -ge $nextCapture) {
                $output = Join-Path $run ('frame-{0:D3}.png' -f $nextCapture)
                $captureArguments = @('--port',$MonitorPort,'--output',$output)
                if ($FtpPort) { $captureArguments += '--auto-framebuffer' }
                & python (Join-Path $PSScriptRoot 'monitor_capture.py') @captureArguments
                if ($LASTEXITCODE -ne 0) { throw 'Guest capture failed.' }
                if ($LaunchXromwell -and -not $launchSent -and $nextCapture -ge 30) {
                    & python (Join-Path $PSScriptRoot 'launch_unleashx.py') --port $FtpPort --output (Join-Path $run 'launch-command.json')
                    if ($LASTEXITCODE -ne 0) { throw 'UnleashX launch command failed.' }
                    $launchSent = $true
                }
                $nextCapture += 15
            }
            Start-Sleep -Milliseconds 250
        }
    } finally {
        if ($vm) { $vm.Refresh(); if (-not $vm.HasExited) { $vm.Kill(); $vm.WaitForExit() } }
        if (Test-Path (Join-Path $run 'instance.json')) {
            & (Join-Path $integration 'complete_xemu_instance.ps1') -RunDirectory $run
        }
        $ownedDisk = [IO.Path]::GetFullPath((Join-Path $run 'hdd.qcow2'))
        if ([IO.Path]::GetDirectoryName($ownedDisk) -ne [IO.Path]::GetFullPath($run)) { throw 'Unexpected staging disk path.' }
        Remove-Item -LiteralPath $ownedDisk -ErrorAction SilentlyContinue
        @{retained=$false; reason='Read-only staging copy; guest used snapshot mode.'} | ConvertTo-Json | Set-Content (Join-Path $run 'disk-retention.json')
    }
}
