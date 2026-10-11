#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$dest=Join-Path $PSScriptRoot process-closure001.json
if(Test-Path -LiteralPath $dest){throw 'Closure record exists'}
$rows=@()
foreach($phase in 244,245){
 $kit=Join-Path $ws "outputs/gpu-lifecycle$phase"
 $m=Get-Content (Join-Path $kit matrix001.json) -Raw | ConvertFrom-Json
 $s=Get-Content (Join-Path $kit preserve001/host-state.json) -Raw | ConvertFrom-Json
 if(-not $s.closed -or -not $s.cleanup_record_exists){throw 'Owned case still active'}
 $closed=[DateTimeOffset]::Parse($m.finished_utc).UtcDateTime
 $run="E:/Codex-private-artifacts/xbox-windows-feasibility/phase$phase-runs/nt5-phase$phase-preserve001"
 $vm=Get-Content (Join-Path $run instance.json) -Raw | ConvertFrom-Json
 $exit=Get-Content (Join-Path $run host-exit.json) -Raw | ConvertFrom-Json
 if(-not $exit.passed){throw 'Orderly owned VM exit missing'}
 $owned=@($m.controller_pid,$s.controller_pid,$s.runner_pid,$s.tracer_pid,$s.observer_pid,$vm.processId)
 foreach($id in ($owned | Sort-Object -Unique)){
  $p=Get-Process -Id $id -ErrorAction SilentlyContinue
  $row=@{id=$id;phase=$phase;old_identity_absent=$true;numeric_pid_absent=(-not $p)}
  if($p){
   if($p.StartTime.ToUniversalTime() -le $closed -or $p.ProcessName -eq "xemu-windows-native-phase$phase"){throw 'Original process may remain'}
   $row.reused_by=$p.ProcessName;$row.new_start_utc=$p.StartTime.ToUniversalTime().ToString('o')
  }
  $rows+=$row
 }
 if(Get-Process -Name "xemu-windows-native-phase$phase" -ErrorAction SilentlyContinue){throw 'Owned VM alive'}
}
@{closed=$true;no_root_guest_queued=$true;processes=$rows;physical_access=$false;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free;unified_sessions=@{build00390573='closed0';build00467046='closed0';build0053548='closed0';matrix24482152='closed1';matrix24519660='closed0'}} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $dest -Encoding utf8
