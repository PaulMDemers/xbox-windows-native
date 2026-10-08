#requires -Version 7.4
$ErrorActionPreference='Stop'
$dest=Join-Path $PSScriptRoot candidate001/lease-check.json
if (Test-Path -LiteralPath $dest) { throw 'Already checked' }
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$instance=Get-Content (Join-Path $ws work/runs/nt5-vlife-candidate001/instance.json) -Raw | ConvertFrom-Json
if ($instance.mode -ne 'exclusive') { throw 'Expected exclusive instance' }
$process=Get-Process -Id $instance.processId -ErrorAction Stop
$results=[ordered]@{checked_utc=[DateTime]::UtcNow.ToString('o');instance_pid=$instance.processId;instance_mode=$instance.mode;build_conflict=$false;xemu_conflict=$false}
foreach ($resource in @('build','xemu')) {
 $lock=Join-Path $env:LOCALAPPDATA ('ogxbox-linux/locks/'+$resource+'.lock')
 if (!(Test-Path -LiteralPath $lock)) { throw 'No resource lock' }
 $handle=$null
 try { $handle=[IO.File]::Open($lock,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None) }
 catch [IO.IOException] { $results[$resource+'_conflict']=$true }
 finally { if ($handle) { $handle.Dispose() } }
}
$results | ConvertTo-Json | Set-Content -LiteralPath $dest -Encoding utf8
if (!$results.build_conflict -or !$results.xemu_conflict) { throw 'Lease isolation did not hold' }
'Both build and exclusive xemu leases block competing acquisition'
