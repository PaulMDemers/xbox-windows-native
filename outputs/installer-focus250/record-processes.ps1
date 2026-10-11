#requires -Version 7.4
$ErrorActionPreference='Stop'
$dest=Join-Path $PSScriptRoot process-closure001.json
if(Test-Path $dest){throw 'Never rewrite process closure'}
$rows=@();$snapshot=@(Get-CimInstance Win32_Process)
foreach($phase in 249,250){
 $kit=Join-Path $PSScriptRoot "../installer-focus$phase"
 $state=Get-Content (Join-Path $kit preserve001/host-state.json) -Raw | ConvertFrom-Json
 if(-not $state.closed -or -not $state.cleanup_record_exists){throw 'Owned case active'}
 $closed=[DateTimeOffset]::Parse($state.closed_utc).UtcDateTime
 $run="E:/Codex-private-artifacts/xbox-windows-feasibility/phase$phase-runs/nt5-phase$phase-preserve001"
 $vm=Get-Content (Join-Path $run instance.json) -Raw | ConvertFrom-Json
 $exit=Get-Content (Join-Path $run host-exit.json) -Raw | ConvertFrom-Json
 if(-not $exit.passed){throw 'Orderly VM exit required'}
 foreach($id in (@($state.controller_pid,$state.runner_pid,$state.tracer_pid,$state.observer_pid,$vm.processId) | Sort-Object -Unique)){
  $p=$snapshot | Where-Object {$_.ProcessId -eq $id};$row=@{phase=$phase;id=$id;old_identity_absent=$true;numeric_pid_absent=(-not $p)}
  if($p){
   if(-not $p.CreationDate -or $p.CreationDate.ToUniversalTime() -le $closed){throw 'Original recorded actor may remain'}
   $row.reused_by=$p.Name;$row.new_start_utc=$p.CreationDate.ToUniversalTime().ToString('o')
  }
  $rows+=$row
 }
 if(Get-Process -Name "xemu-windows-native-phase$phase" -ErrorAction SilentlyContinue){throw 'Owned VM alive'}
}
@{closed=$true;no_guest_queued=$true;processes=$rows;physical_access=$false;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free} | ConvertTo-Json -Depth 7 | Set-Content $dest
