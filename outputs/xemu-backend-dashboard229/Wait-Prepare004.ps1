#requires -Version 7.4
$ErrorActionPreference='Stop'
$dest=Join-Path $PSScriptRoot 'preparation-wait004.json'
if(Test-Path -LiteralPath $dest){throw 'Closed/active wait record exists; inspect instead of repeating'}
$paths=@(
 (Join-Path $PSScriptRoot 'trace001'),
 (Join-Path $PSScriptRoot 'fixture-trace001.json'),
 (Join-Path $PSScriptRoot 'emulator-frozen.json'),
 'E:/Codex-archive/xbox-windows-native/dashboard229/trace001-preparation.qcow2',
 'E:/Codex-archive/xbox-windows-native/dashboard229/trace001-source.qcow2',
 'E:/Codex-private-artifacts/xbox-windows-feasibility/dashboard229-runs/nt5-dashboard229-trace001')
$record=[ordered]@{pid=$PID;started_utc=[DateTime]::UtcNow.ToString('o');script_sha256=(Get-FileHash $PSCommandPath).Hash;attempts=@();closed=$false;prepared=$false;guest_launched=$false;physical_access=$false}
function Save-Wait {
 $temporary=$dest+'.tmp'
 $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $temporary -Encoding utf8
 Move-Item -LiteralPath $temporary -Destination $dest -Force
}
$clock=[Diagnostics.Stopwatch]::StartNew()
try {
 Save-Wait
 while($true){
  foreach($path in $paths){if(Test-Path -LiteralPath $path){throw ('Identity exists before preparation: '+$path)}}
  try {
   & (Join-Path $PSScriptRoot 'Prepare.ps1') -Case trace001
   $record.prepared=$true
   break
  } catch {
   $busy=$_.Exception.Message -like "Xbox resource 'build' is busy or unavailable*"
   $created=@($paths | Where-Object {Test-Path -LiteralPath $_})
   $record.attempts+=@{utc=[DateTime]::UtcNow.ToString('o');resource_busy=$busy;created_paths=$created;error=$_.Exception.Message}
   Save-Wait
   if(-not $busy -or $created.Count){throw}
   if($clock.Elapsed.TotalSeconds -ge 600){throw 'Cooperative wait expired before any preparation artifact'}
   Start-Sleep -Seconds 15
  }
 }
} catch {
 $record.error=$_.Exception.Message
 throw
} finally {
 $record.closed=$true
 $record.closed_utc=[DateTime]::UtcNow.ToString('o')
 Save-Wait
}
