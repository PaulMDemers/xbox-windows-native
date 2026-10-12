#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$cache='C:\Users\Paul\AppData\Local\ogxbox-linux\instances'
$archive='E:\Codex-archive\xbox-windows-native\closed-portable-299b'
$record=Join-Path $PSScriptRoot 'portable-299b.json'
if((Test-Path -LiteralPath $archive) -or (Test-Path -LiteralPath $record)){throw 'Never repeat offload'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  if(Get-Process -Name xemu* -ErrorAction SilentlyContinue){throw 'An emulator is active'}
  $plan=Get-Content (Join-Path $PSScriptRoot plan-299b.json) -Raw | ConvertFrom-Json
  $rows=@();$total=0L
  foreach($item in $plan){
   $source=Join-Path (Join-Path $cache $item.task) '685F24E317322469'
   $source=[IO.Path]::GetFullPath($source)
   if(-not $source.StartsWith($cache+'\') -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Source outside owned cache or already offloaded'}
   $closures=@()
   foreach($run in $item.runs){
    $absolute=[IO.Path]::GetFullPath($run)
    if(-not $absolute.StartsWith((Join-Path $ws 'work\runs')+'\')){throw 'Run boundary mismatch'}
    $meta=Get-Content (Join-Path $absolute instance.json) -Raw | ConvertFrom-Json
    $close=Join-Path $absolute cleanup.json
    if($meta.taskId -ne $item.task -or $meta.portableRoot -ne $source -or -not (Test-Path -LiteralPath $close)){throw 'Owned closed instance mismatch'}
    $closures+=@{path=$close;sha256=(Get-FileHash -LiteralPath $close).Hash.ToLowerInvariant()}
   }
   if(@(Get-ChildItem -LiteralPath $source -Recurse | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Nested reparse point'}
   $files=@(Get-ChildItem -LiteralPath $source -Recurse -File)
   if(@($files | Where-Object {$_.Extension -in '.qcow2','.iso','.img','.raw','.vhd','.vhdx'}).Count){throw 'Backing media forbidden'}
   $pins=@($files | ForEach-Object {@{path=$_.FullName.Substring($source.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
   $total+=($files | Measure-Object Length -Sum).Sum
   $rows+=@{source=$source;target=(Join-Path $archive $item.task);files=$pins;closures=$closures;completed=$false}
  }
  if((Get-PSDrive E).Free-$total-128MB -lt 20GB){throw 'Destination projected reserve'}
  New-Item -ItemType Directory -Path $archive | Out-Null
  $report=@{rows=$rows;bytes=$total;disk_backing_chains_moved=$false;completed=$false}
  $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $record -Encoding utf8
  foreach($row in $rows){
   New-Item -ItemType Directory -Path $row.target | Out-Null
   foreach($entry in (Get-ChildItem -LiteralPath $row.source)){Copy-Item -LiteralPath $entry.FullName -Destination $row.target -Recurse}
   if(@(Get-ChildItem -LiteralPath $row.target -Recurse -File).Count -ne $row.files.Count){throw 'Copy inventory mismatch'}
   foreach($pin in $row.files){$p=Join-Path $row.target $pin.path;if((Get-Item -LiteralPath $p).Length -ne $pin.bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $pin.sha256){throw 'Copy verification failed'}}
   $absolute=[IO.Path]::GetFullPath($row.source)
   if($absolute -ne $row.source -or -not $absolute.StartsWith($cache+'\') -or (Get-Item -LiteralPath $absolute).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Removal boundary changed'}
   foreach($pin in $row.files){if((Get-FileHash -LiteralPath (Join-Path $absolute $pin.path)).Hash.ToLowerInvariant() -ne $pin.sha256){throw 'Original changed before removal'}}
   Remove-Item -LiteralPath $absolute -Recurse
   New-Item -ItemType Junction -Path $absolute -Target $row.target | Out-Null
   foreach($pin in $row.files){if((Get-FileHash -LiteralPath (Join-Path $absolute $pin.path)).Hash.ToLowerInvariant() -ne $pin.sha256){throw 'Original-path readback failed'}}
   $row.completed=$true
   $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $record -Encoding utf8
  }
  $report.completed=$true;$report.free_c=(Get-PSDrive C).Free;$report.free_e=(Get-PSDrive E).Free
  $report | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $record -Encoding utf8
  Write-Output "Verified $($rows.Count) closed non-backing portables; $total bytes recovered"
 }
}
