#requires -Version 7.4
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidatePattern('^[a-z][a-z0-9-]{0,39}$')][string]$TaskId,
    [Parameter(Mandatory)][string]$XemuPath,
    [Parameter(Mandatory)][string]$ConfigPath,
    [Parameter(Mandatory)][string]$RunDirectory,
    [string[]]$ArgumentList = @(),
    [string]$StandardOutputPath,
    [string]$StandardErrorPath,
    [string]$ScratchRoot,
    [string]$InstanceRoot = (Join-Path $env:LOCALAPPDATA 'ogxbox-linux\instances')
)
$ErrorActionPreference = 'Stop'
. 'C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/xemu_instance.ps1'
. 'C:/Users/Paul/Desktop/ogxbox-linux/scripts/lib/test_storage.ps1'
if ($env:XBOX_XEMU_MODE -notin @('shared','exclusive')) {
    throw 'Launch inside with_xbox_resource.ps1 -Resource xemu; hold its lease until the returned process exits.'
}
if ($ArgumentList -contains '-config_path') { throw 'Use ConfigPath, not a second -config_path argument.' }
$source = (Resolve-Path -LiteralPath $XemuPath).Path
$config = (Resolve-Path -LiteralPath $ConfigPath).Path
$run = [IO.Path]::GetFullPath($RunDirectory)
New-Item -ItemType Directory -Force -Path $run | Out-Null
$manifestPath = Join-Path $run 'instance.json'
$runtimeConfig = Join-Path $run 'instance-config.toml'
if ((Test-Path -LiteralPath $manifestPath) -or (Test-Path -LiteralPath $runtimeConfig)) {
    throw 'Instance run directory already used; choose a fresh run directory.'
}
$hash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash
$portable = Join-Path ([IO.Path]::GetFullPath($InstanceRoot)) "$TaskId\$($hash.Substring(0,16))"
$executable = Join-Path $portable "xemu-$TaskId.exe"
if (Get-Process -Name "xemu-$TaskId" -ErrorAction SilentlyContinue) { throw "Task $TaskId already has an emulator process." }
New-Item -ItemType Directory -Force -Path $portable | Out-Null
if (-not (Test-Path -LiteralPath $executable)) { Copy-Item -LiteralPath $source -Destination $executable }
if ((Get-FileHash -LiteralPath $executable -Algorithm SHA256).Hash -ne $hash) { throw 'Private emulator copy hash mismatch.' }
foreach ($name in @('LICENSE.txt','build-provenance.txt')) {
    $inputFile = Join-Path (Split-Path -Parent $source) $name
    if (Test-Path -LiteralPath $inputFile) { Copy-Item -LiteralPath $inputFile -Destination (Join-Path $portable $name) -Force }
}
# xemu detects portable mode from this file even when -config_path is explicit.
[IO.File]::WriteAllText((Join-Path $portable 'xemu.toml'), "[general]`nshow_welcome = false`n[general.updates]`ncheck = false`n", [Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText($runtimeConfig, (Disable-XboxXemuUpdates ([IO.File]::ReadAllText($config))), [Text.UTF8Encoding]::new($false))
if (-not $StandardOutputPath) { $StandardOutputPath = Join-Path $run 'xemu-stdout.log' }
if (-not $StandardErrorPath) { $StandardErrorPath = Join-Path $run 'xemu-stderr.log' }
# Match CommandLineToArgvW quoting, including embedded quotes and trailing slashes.
function Quote-WindowsArgument([string]$Value) {
    '"' + ([regex]::Replace([regex]::Replace($Value, '(\\*)"', '$1$1\"'), '(\\+)$', '$1$1')) + '"'
}
$arguments = @('-config_path', $runtimeConfig) + $ArgumentList
$commandLine = ($arguments | ForEach-Object { Quote-WindowsArgument $_ }) -join ' '
if (-not $ScratchRoot) {
    $ScratchRoot = Get-XboxWindowsScratchRoot -RepoRoot (Split-Path -Parent $PSScriptRoot) -DefaultRoot (Join-Path $run 'scratch')
}
if (-not [IO.Path]::IsPathFullyQualified($ScratchRoot)) { throw 'ScratchRoot must be an absolute path.' }
$ScratchRoot = [IO.Path]::GetFullPath($ScratchRoot)
$scratch = Join-Path $ScratchRoot ($TaskId + '-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $scratch -Force | Out-Null
[ordered]@{taskId=$TaskId; runDirectory=$run; scratchDirectory=$scratch} | ConvertTo-Json |
    Set-Content -LiteralPath (Join-Path $scratch '.ogxbox-scratch.json') -Encoding utf8
$process = $null
try {
    # Scope QEMU snapshot overlays to this VM, without changing the parent shell
    # or other concurrently running emulators. QCOW2 temp files work on exFAT.
    $process = Start-Process -FilePath $executable -ArgumentList $commandLine -WorkingDirectory $run `
        -Environment @{TEMP=$scratch; TMP=$scratch; TMPDIR=$scratch} `
        -WindowStyle Hidden -PassThru -RedirectStandardOutput $StandardOutputPath -RedirectStandardError $StandardErrorPath
    $title = "ogxbox | $TaskId | PID $($process.Id)"
    $metadata = [ordered]@{taskId=$TaskId; processId=$process.Id; windowTitle=$title;
        executable=$executable; sourceSha256=$hash; portableRoot=$portable; config=$runtimeConfig;
        scratchRoot=$ScratchRoot; scratchDirectory=$scratch;
        mode=$env:XBOX_XEMU_MODE; slot=$env:XBOX_XEMU_SLOT; startedUtc=$process.StartTime.ToUniversalTime().ToString('o')}
    [IO.File]::WriteAllText($manifestPath, ($metadata | ConvertTo-Json), [Text.UTF8Encoding]::new($false))
    $timer = [Diagnostics.Stopwatch]::StartNew()
    do {
        $process.Refresh()
        if ($process.HasExited) { throw "xemu exited before window creation; inspect $StandardErrorPath" }
        if ($process.MainWindowHandle -ne [IntPtr]::Zero) { break }
        Start-Sleep -Milliseconds 100
    } while ($timer.Elapsed.TotalSeconds -lt 30)
    Set-XboxXemuWindowTitle -Process $process -Title $title
    $process
} catch {
    if ($process -and -not $process.HasExited) { $process.Kill(); $process.WaitForExit() }
    Remove-XboxTestPath -Root $ScratchRoot -Path $scratch
    throw
}
