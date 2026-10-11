#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$source=[IO.Path]::GetFullPath((Join-Path $ws 'outputs/gpu-reference-snapshot238/artifacts/build001'))
$expected=$ws+'\outputs\gpu-reference-snapshot238\artifacts\build001'
if($source -ne $expected -or -not $source.StartsWith($ws+'\')){throw 'Resolved target outside exact owned closed build'}
if((Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Already linked; never repeat offload'}
$old=Get-Content (Join-Path $ws 'outputs/gpu-reference-snapshot238/owned-pids001.json') -Raw | ConvertFrom-Json
$closed=Get-Content (Join-Path $ws 'outputs/gpu-reference-snapshot238/matrix001.json') -Raw | ConvertFrom-Json
$closedTime=[DateTimeOffset]::Parse($closed.finished_utc).UtcDateTime
if(-not $closed.closed -or -not $closed.completed){throw 'Closed matrix proof missing'}
$reused=@()
foreach($id in $old.ids){
 $p=Get-Process -Id $id -ErrorAction SilentlyContinue
 if($p){
  if($p.StartTime.ToUniversalTime() -le $closedTime -or $p.ProcessName -eq 'xemu-windows-native-phase238'){throw 'Old process identity still possible; inspect before moving'}
  $reused+=@{id=$id;name=$p.ProcessName;start_utc=$p.StartTime.ToUniversalTime().ToString('o');old_matrix_closed_utc=$closed.finished_utc;numeric_pid_reused=$true}
 }
}
$target='E:\Codex-archive\xbox-windows-native\closed-builds\phase238-build001'
if(Test-Path -LiteralPath $target){throw 'Unique destination already exists'}
$items=Get-ChildItem -LiteralPath $source -File -Recurse
if($items | Where-Object {$_.Extension -in '.qcow2','.vhd','.img','.iso'}){throw 'Disk backing/media not allowed in this artifact move'}
$rows=@($items | ForEach-Object {@{path=$_.FullName.Substring($source.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
$sum=($rows | Measure-Object -Property bytes -Sum).Sum
if((Get-PSDrive E).Free - $sum -lt 20GB){throw 'E capacity guard'}
New-Item -ItemType Directory -Path $target | Out-Null
foreach($entry in (Get-ChildItem -LiteralPath $source)){Copy-Item -LiteralPath $entry.FullName -Destination $target -Recurse}
foreach($row in $rows){
 $p=Join-Path $target $row.path
 if((Get-Item -LiteralPath $p).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Destination byte verification failed; source preserved'}
}
if(@(Get-ChildItem -LiteralPath $target -File -Recurse).Count -ne $rows.Count){throw 'Destination inventory differs'}
# Repeat the exact resolved workspace boundary immediately before recursive removal.
if([IO.Path]::GetFullPath($source) -ne $expected -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Source boundary changed'}
Remove-Item -LiteralPath $source -Recurse
New-Item -ItemType Junction -Path $source -Target $target | Out-Null
foreach($row in $rows){if((Get-FileHash -LiteralPath (Join-Path $source $row.path)).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Original path readback mismatch'}}
@{closed=$true;source=$source;target=$target;bytes=$sum;files=$rows;all_hashes_verified=$true;original_path_preserved=$true;disk_backing_chains_moved=$false;reused_process_ids=$reused;physical_access=$false;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $PSScriptRoot offload-build001.json) -Encoding utf8
Write-Output "Closed238 build offload verified: $sum bytes"
