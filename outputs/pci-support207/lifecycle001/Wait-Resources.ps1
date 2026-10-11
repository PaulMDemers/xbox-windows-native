#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('run','hal')][string]$Task)
$ErrorActionPreference='Stop'
$script=if($Task -eq 'run'){Join-Path $PSScriptRoot 'Run-Emulator001.ps1'}else{Join-Path $PSScriptRoot '../handoff001/Build-001.ps1'}
$record=Join-Path $PSScriptRoot "lease-$Task-001.json"
if(Test-Path -LiteralPath $record){throw 'Fresh waiter journal required'}
$rows=@()
for($i=0;$i -lt 24;$i++){
 try {
  & $script
  $rows+=@{utc=[DateTime]::UtcNow.ToString('o');result='action_completed'}
  $rows|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $record
  exit 0
 } catch {
  $message=$_.Exception.Message
  $busy=$message -like "Xbox resource '*' is busy or unavailable*"
  $rows+=@{utc=[DateTime]::UtcNow.ToString('o');result=if($busy){'lease_busy_no_action'}else{'action_failed'};message=$message}
  $rows|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $record
  if(!$busy){throw}
 }
 Start-Sleep -Seconds 20
}
throw 'Bounded lease wait expired without action'
