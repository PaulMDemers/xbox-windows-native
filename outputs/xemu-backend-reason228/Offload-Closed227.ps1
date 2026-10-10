#requires -Version 7.4
# Hash-verified closed build artifacts only; no disk backing chains involved.
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../xemu-backend-preserve227'))
$taskDestination='E:\Codex-private-artifacts\xbox-windows-feasibility\preserve227-builds'
$taskManifest=Join-Path $taskRoot 'closed-build005-offload.json'
if(Test-Path -LiteralPath $taskManifest){throw 'Offload already recorded'}
if(-not ((Get-Content (Join-Path $taskRoot 'trace001/host-state.json') -Raw | ConvertFrom-Json).closed)){throw '227 runtime not closed'}
$taskRows=@()
foreach($taskId in @('build005')) {
 $taskRecord=Get-Content -LiteralPath (Join-Path $taskRoot ($taskId+'.json')) -Raw | ConvertFrom-Json
 if(-not $taskRecord.passed -or -not $taskRecord.borrowed_sources_restored){throw 'Build not closed'}
 $taskSource=[IO.Path]::GetFullPath((Join-Path $taskRoot ('artifacts/'+$taskId)))
 $taskTarget=[IO.Path]::GetFullPath((Join-Path $taskDestination $taskId))
 $taskBackup=[IO.Path]::GetFullPath($taskSource+'-verified-backup')
 if(-not $taskSource.StartsWith($taskRoot+'\') -or -not $taskBackup.StartsWith($taskRoot+'\') -or -not $taskTarget.StartsWith($taskDestination+'\')){throw 'Containment failed'}
 if((Get-Item -LiteralPath $taskSource).LinkType -or (Test-Path -LiteralPath $taskTarget) -or (Test-Path -LiteralPath $taskBackup)){throw 'Unexpected source/target state'}
 $taskHashes=[ordered]@{}
 Get-ChildItem -LiteralPath $taskSource -Recurse -File | ForEach-Object {
  if($_.Extension -in '.qcow2','.vhd','.img'){throw 'No backing chains or images permitted'}
  $taskRelative=[IO.Path]::GetRelativePath($taskSource,$_.FullName)
  $taskHashes[$taskRelative]=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()
 }
 New-Item -ItemType Directory -Path $taskDestination -Force | Out-Null
 Copy-Item -LiteralPath $taskSource -Destination $taskTarget -Recurse
 foreach($taskName in $taskHashes.Keys){if((Get-FileHash -LiteralPath (Join-Path $taskTarget $taskName)).Hash.ToLowerInvariant() -ne $taskHashes[$taskName]){throw 'Target readback mismatch'}}
 Move-Item -LiteralPath $taskSource -Destination $taskBackup
 New-Item -ItemType Junction -Path $taskSource -Target $taskTarget | Out-Null
 foreach($taskName in $taskHashes.Keys){if((Get-FileHash -LiteralPath (Join-Path $taskSource $taskName)).Hash.ToLowerInvariant() -ne $taskHashes[$taskName]){throw 'Junction readback mismatch'}}
 $taskResolvedBackup=[IO.Path]::GetFullPath((Get-Item -LiteralPath $taskBackup).FullName)
 if($taskResolvedBackup -ne $taskBackup -or -not $taskResolvedBackup.StartsWith($taskRoot+'\') -or (Get-Item -LiteralPath $taskBackup).LinkType){throw 'Unsafe backup deletion refused'}
 Remove-Item -LiteralPath $taskResolvedBackup -Recurse
 $taskRows+=@{id=$taskId;status='closed_audited_diagnostic_build_offloaded_verified';source=$taskSource;target=$taskTarget;hashes=$taskHashes}
 @{records=$taskRows;C_free_bytes=(Get-PSDrive C).Free;E_free_bytes=(Get-PSDrive E).Free} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $taskManifest -Encoding utf8
}

