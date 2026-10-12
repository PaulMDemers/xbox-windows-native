#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws='C:\Users\Paul\Documents\Codex\2026-10-02\xbox-windows-feasibility'
$cache='C:\Users\Paul\AppData\Local\ogxbox-linux\instances'
$source=Join-Path $cache 'windows-native-word186\685F24E317322469'
$dest='E:\Codex-archive\xbox-windows-native\closed-portable-278'
if(Test-Path -LiteralPath $dest){throw 'Never repeat offload'}
foreach($case in @('control001','candidate001')){
 $run=Join-Path $ws "work/runs/nt5-word186-$case"
 $closure=Get-Content (Join-Path $ws "outputs/video-word-order186/$case/closure.json") -Raw | ConvertFrom-Json
 $meta=Get-Content (Join-Path $run instance.json) -Raw | ConvertFrom-Json
 if(-not $closure.closed -or $meta.taskId -ne 'windows-native-word186' -or $meta.portableRoot -ne $source){throw 'Owned closure/portable identity mismatch'}
 if((Get-FileHash -LiteralPath (Join-Path $run cleanup.json)).Hash.ToLowerInvariant() -ne $closure.cleanup_sha256){throw 'Cleanup mismatch'}
}
if(Get-Process -Name xemu-windows-native-word186 -ErrorAction SilentlyContinue){throw 'Owned process active'}
$resolved=[IO.Path]::GetFullPath($source)
if($resolved -ne $source -or -not $resolved.StartsWith($cache+'\') -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Unexpected source boundary'}
if(@(Get-ChildItem -LiteralPath $source -Recurse | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Nested junction'}
$items=@(Get-ChildItem -LiteralPath $source -Recurse -File)
if(@($items | Where-Object {$_.Extension -in '.qcow2','.iso','.img','.vhd','.vhdx','.raw'}).Count){throw 'Backing media forbidden'}
$rows=@($items | ForEach-Object {@{path=$_.FullName.Substring($source.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
New-Item -ItemType Directory -Path $dest | Out-Null
foreach($entry in (Get-ChildItem -LiteralPath $source)){Copy-Item -LiteralPath $entry.FullName -Destination $dest -Recurse}
if(@(Get-ChildItem -LiteralPath $dest -Recurse -File).Count -ne $rows.Count){throw 'Copy inventory mismatch'}
foreach($row in $rows){$p=Join-Path $dest $row.path;if((Get-Item -LiteralPath $p).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Copy hash mismatch'}}
if([IO.Path]::GetFullPath($source) -ne $resolved -or -not $resolved.StartsWith($cache+'\') -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Removal boundary changed'}
Remove-Item -LiteralPath $source -Recurse
New-Item -ItemType Junction -Path $source -Target $dest | Out-Null
foreach($row in $rows){if((Get-FileHash -LiteralPath (Join-Path $source $row.path)).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Original path readback mismatch'}}
@{source=$source;target=$dest;files=$rows;original_path_preserved=$true;owned_vm_closed=$true;disk_backing_chains_moved=$false;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $ws 'outputs/task-storage-offload/portable-278.json') -Encoding utf8
Write-Output 'Closed186 portable hash-verified on E; original path preserved'
