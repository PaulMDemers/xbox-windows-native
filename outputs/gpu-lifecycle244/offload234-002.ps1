#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$old=Join-Path $ws 'outputs/xemu-wait-snapshot234'
$run='E:/Codex-private-artifacts/xbox-windows-feasibility/snapshot234-runs/nt5-snapshot234-trace002'
$hostState=Get-Content (Join-Path $old 'trace002/host-state.json') -Raw | ConvertFrom-Json
$meta=Get-Content (Join-Path $run 'instance.json') -Raw | ConvertFrom-Json
if(-not $hostState.closed -or -not (Test-Path (Join-Path $run 'cleanup.json'))){throw 'Closed owned run required'}
$oldProcess=Get-Process -Id $meta.processId -ErrorAction SilentlyContinue
if($oldProcess -and $oldProcess.StartTime.ToUniversalTime() -le [DateTimeOffset]::Parse($hostState.closed_utc).UtcDateTime){throw 'Original VM identity still present'}
if($meta.taskId -ne 'windows-native-snapshot234' -or (Get-Process -Name 'xemu-windows-native-snapshot234' -ErrorAction SilentlyContinue)){throw 'Portable still active'}
$dest='E:\Codex-archive\xbox-windows-native\closed-artifacts-244'
if(Test-Path -LiteralPath $dest){throw 'Never repeat completed/partial offload'}
$cache='C:\Users\Paul\AppData\Local\ogxbox-linux\instances'
$portable=[IO.Path]::GetFullPath($meta.portableRoot)
$expected=Join-Path (Join-Path $cache $meta.taskId) $meta.sourceSha256.Substring(0,16)
if($portable -ne $expected){throw 'Unexpected portable boundary'}
$build=[IO.Path]::GetFullPath((Join-Path $old 'artifacts/build001'))
$approved=@($build,$expected)
$targets=@((Join-Path $dest 'build234'),(Join-Path $dest 'portable234'))
$entries=@()
for($i=0;$i -lt 2;$i++){
 $source=[IO.Path]::GetFullPath($approved[$i]);$target=[IO.Path]::GetFullPath($targets[$i])
 if($source -ne $approved[$i] -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Exact source or reparse boundary refused'}
 $files=@(Get-ChildItem -LiteralPath $source -File -Recurse)
 if(@($files | Where-Object {$_.Extension -in '.qcow2','.img','.vhd','.iso'}).Count){throw 'Never move backing chains'}
 $rows=@($files | ForEach-Object {@{path=$_.FullName.Substring($source.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
 New-Item -ItemType Directory -Path $target -Force | Out-Null
 foreach($entry in (Get-ChildItem -LiteralPath $source)){Copy-Item -LiteralPath $entry.FullName -Destination $target -Recurse}
 if(@(Get-ChildItem -LiteralPath $target -File -Recurse).Count -ne $rows.Count){throw 'File count differs'}
 foreach($row in $rows){$p=Join-Path $target $row.path;if((Get-Item -LiteralPath $p).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Copy readback failure; source preserved'}}
 if([IO.Path]::GetFullPath($source) -ne $approved[$i] -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Deletion boundary changed'}
 Remove-Item -LiteralPath $source -Recurse
 New-Item -ItemType Junction -Path $source -Target $target | Out-Null
 foreach($row in $rows){if((Get-FileHash -LiteralPath (Join-Path $source $row.path)).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Original path readback failure'}}
 $entries+=@{source=$source;target=$target;files=$rows;original_path_preserved=$true;owned_vm_closed=$true;disk_backing_chains_moved=$false}
}
@{closed=$true;entries=$entries;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free;physical_access=$false} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $PSScriptRoot 'offload234.json') -Encoding utf8
