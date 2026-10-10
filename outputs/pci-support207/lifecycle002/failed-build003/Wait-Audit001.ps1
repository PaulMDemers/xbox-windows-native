#requires -Version 7.4
$ErrorActionPreference='Stop'
$record=Join-Path $PSScriptRoot 'lease-audit-001.json'
if(Test-Path -LiteralPath $record){throw 'Fresh waiter journal required'}
$rows=@()
for($i=0;$i -lt 45;$i++){
 try {
  & (Join-Path $PSScriptRoot 'Audit-Pnp001.ps1')
  $rows+=@{utc=[DateTime]::UtcNow.ToString('o');result='action_completed'}
  $rows|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $record
  exit 0
 } catch {
  $message=$_.Exception.Message
  $busy=$message -like "Xbox resource 'build' is busy or unavailable*"
  $rows+=@{utc=[DateTime]::UtcNow.ToString('o');result=if($busy){'lease_busy_no_action'}else{'action_failed'};message=$message}
  $rows|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $record
  if(!$busy){throw}
 }
 Start-Sleep -Seconds 20
}
throw 'Bounded audit lease wait expired without action'
