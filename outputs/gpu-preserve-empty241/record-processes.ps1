#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$dest=Join-Path $PSScriptRoot process-closure001.json
if(Test-Path -LiteralPath $dest){throw 'Closure record exists'}
$rows=@();$ids=@()
foreach($pair in @(@('gpu-preserve-entry239',239),@('gpu-preserve-entry240',240),@('gpu-preserve-empty241',241))){
 $kit=Join-Path (Join-Path $ws outputs) $pair[0]
 $matrix=Get-Content (Join-Path $kit matrix001.json) -Raw | ConvertFrom-Json
 $closed=[DateTimeOffset]::Parse($matrix.finished_utc).UtcDateTime
 $owned=@($matrix.controller_pid)
 foreach($case in $matrix.cases){
  $hostState=Get-Content (Join-Path (Join-Path $kit $case.case) host-state.json) -Raw | ConvertFrom-Json
  if(-not $hostState.closed){throw 'Owned controller not closed'}
  $owned+=@($case.controller_pid,$hostState.runner_pid,$hostState.tracer_pid,$hostState.observer_pid) | Where-Object {$_}
  $run="E:/Codex-private-artifacts/xbox-windows-feasibility/phase$($pair[1])-runs/nt5-phase$($pair[1])-$($case.case)"
  if(Test-Path -LiteralPath (Join-Path $run instance.json)){$owned+=(Get-Content (Join-Path $run instance.json) -Raw | ConvertFrom-Json).processId}
 }
 foreach($id in ($owned | Sort-Object -Unique)){
  $p=Get-Process -Id $id -ErrorAction SilentlyContinue
  $row=@{id=$id;kit=$pair[0];old_identity_absent=$true;numeric_pid_absent=(-not $p);matrix_finished_utc=$matrix.finished_utc}
  if($p){
   if($p.StartTime.ToUniversalTime() -le $closed -or $p.ProcessName -eq "xemu-windows-native-phase$($pair[1])"){throw 'Old owned process identity may still live; never claim closure'}
   $row.reused_by=$p.ProcessName;$row.new_start_utc=$p.StartTime.ToUniversalTime().ToString('o')
  }
  $rows+=$row;$ids+=$id
 }
 if(Get-Process -Name "xemu-windows-native-phase$($pair[1])" -ErrorAction SilentlyContinue){throw 'Owned VM remains active'}
}
@{closed=$true;no_root_guest_queued=$true;ids=@($ids | Sort-Object -Unique);processes=$rows;physical_access=$false;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $dest -Encoding utf8
Write-Output 'All239/240/241 recorded root process identities closed'
