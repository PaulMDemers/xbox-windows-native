#requires -Version 7.4
# Recovery of the same owned instance BEFORE any Windows launch request.
$ErrorActionPreference='Stop'
$taskOut=Join-Path $PSScriptRoot 'trace001'
$taskRun='E:/Codex-private-artifacts/xbox-windows-feasibility/reason228-runs/nt5-reason228-trace001'
$taskRecord=Join-Path $taskOut 'observer-recovery.json'
if(Test-Path -LiteralPath $taskRecord){throw 'Recovery already recorded'}
if((Test-Path (Join-Path $taskOut 'launch.json')) -or (Test-Path (Join-Path $taskRun 'cleanup.json')) -or (Test-Path (Join-Path $taskOut 'trace-finished.signal'))){throw 'Cannot recover after launch/trace/closure'}
if(-not (Test-Path (Join-Path $taskOut 'trace-armed.signal'))){throw 'Existing tracer not armed'}
$taskState=Get-Content (Join-Path $taskOut 'host-state.json') -Raw | ConvertFrom-Json
if(Get-Process -Id $taskState.observer_pid -ErrorAction SilentlyContinue){throw 'Original observer still alive'}
Get-Process -Id $taskState.tracer_pid -ErrorAction Stop | Out-Null
$taskFailure=Get-Content (Join-Path $taskOut 'observer-console.txt') -Raw
if($taskFailure -notmatch "KeyError: 'XWN_EMULATOR_FTP_USER'"){throw 'Unexpected observer failure'}
$taskData=@{status='same_instance_prelaunch_observer_recovery';pid=$PID;original_observer_pid=$taskState.observer_pid;failure_sha256=(Get-FileHash (Join-Path $taskOut 'observer-console.txt')).Hash.ToLowerInvariant();no_previous_windows_request=$true;utc=[DateTime]::UtcNow.ToString('o');physical_access=$false}
$taskData | ConvertTo-Json | Set-Content -LiteralPath $taskRecord -Encoding utf8
# Owned loopback dashboard credentials only, inherited by this one observer.
$env:XWN_EMULATOR_FTP_USER='xbox'
$env:XWN_EMULATOR_FTP_PASSWORD='xbox'
$env:PYTHONUTF8='1'
& C:/Python314/python.exe -B (Join-Path $PSScriptRoot 'supervise-emulator.py') trace001 *> (Join-Path $taskOut 'observer-recovery-console.txt')
$taskData.exit_code=$LASTEXITCODE
$taskData.closed=$true
$taskData.closed_utc=[DateTime]::UtcNow.ToString('o')
$taskData | ConvertTo-Json | Set-Content -LiteralPath $taskRecord -Encoding utf8
if($LASTEXITCODE -ne 0){throw 'Recovered observer failure; preserve same instance'}
