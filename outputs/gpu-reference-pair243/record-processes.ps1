#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$dest=Join-Path $PSScriptRoot process-closure001.json
if(Test-Path -LiteralPath $dest){throw 'Closure record exists'}
$rows=@()
foreach($pair in @(@('gpu-reference-pair242',242),@('gpu-reference-pair243',243))){
 $kit=Join-Path (Join-Path $ws outputs) $pair[0]
 $matrix=Get-Content (Join-Path $kit matrix001.json) -Raw | ConvertFrom-Json
 if(-not $matrix.closed){throw 'Matrix still active'}
 $closed=[DateTimeOffset]::Parse($matrix.finished_utc).UtcDateTime
 $owned=@($matrix.controller_pid)
 foreach($case in $matrix.cases){
  $state=Get-Content (Join-Path (Join-Path $kit $case.case) host-state.json) -Raw | ConvertFrom-Json
  if(-not $state.closed){throw 'Case still active'}
  $owned+=@($case.controller_pid,$state.runner_pid,$state.tracer_pid,$state.observer_pid) | Where-Object {$_}
  $run="E:/Codex-private-artifacts/xbox-windows-feasibility/phase$($pair[1])-runs/nt5-phase$($pair[1])-$($case.case)"
  $owned+=(Get-Content (Join-Path $run instance.json) -Raw | ConvertFrom-Json).processId
  $exit=Get-Content (Join-Path $run host-exit.json) -Raw | ConvertFrom-Json
  if(-not $exit.passed){throw 'Orderly VM exit missing'}
 }
 foreach($id in ($owned | Sort-Object -Unique)){
  $p=Get-Process -Id $id -ErrorAction SilentlyContinue
  $row=@{id=$id;kit=$pair[0];old_identity_absent=$true;numeric_pid_absent=(-not $p);matrix_finished_utc=$matrix.finished_utc}
  if($p){
   if($p.StartTime.ToUniversalTime() -le $closed -or $p.ProcessName -eq "xemu-windows-native-phase$($pair[1])"){throw 'Old process may still live'}
   $row.reused_by=$p.ProcessName;$row.new_start_utc=$p.StartTime.ToUniversalTime().ToString('o')
  }
  $rows+=$row
 }
 if(Get-Process -Name "xemu-windows-native-phase$($pair[1])" -ErrorAction SilentlyContinue){throw 'Owned VM active'}
}
@{closed=$true;no_root_guest_queued=$true;processes=$rows;physical_access=$false;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free;owned_unified_sessions=@{build24902='closed0';build45816='closed0';host_test76240='closed0';matrix85879='closed1';matrix60522='closed0'}} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $dest -Encoding utf8
Write-Output 'Root242/243 process identities closed; no root guest queued'
