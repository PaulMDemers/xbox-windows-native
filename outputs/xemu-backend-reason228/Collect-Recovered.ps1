#requires -Version 7.4
$ErrorActionPreference='Stop'
$taskOut=Join-Path $PSScriptRoot 'trace001'
$taskRun='E:/Codex-private-artifacts/xbox-windows-feasibility/reason228-runs/nt5-reason228-trace001'
$taskRecord=Join-Path $taskOut 'recovered-closure.json'
if(Test-Path -LiteralPath $taskRecord){throw 'Recovery cold collection already recorded'}
$taskState=Get-Content (Join-Path $taskOut 'host-state.json') -Raw | ConvertFrom-Json
$taskRecovery=Get-Content (Join-Path $taskOut 'observer-recovery.json') -Raw | ConvertFrom-Json
if(-not $taskState.closed -or -not $taskRecovery.closed -or -not (Test-Path (Join-Path $taskRun 'cleanup.json'))){throw 'Owned processes not closed'}
foreach($taskId in @($taskState.controller_pid,$taskState.runner_pid,$taskState.tracer_pid,$taskState.observer_pid,$taskRecovery.pid)){
 if(Get-Process -Id $taskId -ErrorAction SilentlyContinue){throw 'Owned PID still alive'}
}
if(Test-Path (Join-Path $taskOut 'audit.json')){throw 'Audit already exists; do not recollect'}
$taskData=@{status='recovering_cold_audit_once';pid=$PID;utc=[DateTime]::UtcNow.ToString('o');original_controller_status=$taskState.status;original_controller_error=$taskState.error;physical_access=$false;ordinary_qualified=$false}
$taskData | ConvertTo-Json | Set-Content -LiteralPath $taskRecord -Encoding utf8
$taskScript=$PSScriptRoot.Replace('\','/').Replace('C:','/mnt/c')+'/audit-emulator.py'
& wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 -B $taskScript trace001 *> (Join-Path $taskOut 'recovered-cold-audit-console.txt')
$taskData.audit_exit_code=$LASTEXITCODE
$taskData.closed=$true
$taskData.closed_utc=[DateTime]::UtcNow.ToString('o')
$taskData.status=if($LASTEXITCODE -eq 0){'cold_audited_closed_with_original_harness_failure'}else{'failed_cold_audit_preserved'}
$taskData | ConvertTo-Json | Set-Content -LiteralPath $taskRecord -Encoding utf8
if($LASTEXITCODE -ne 0){throw 'Recovered cold audit failed; never rerun'}
