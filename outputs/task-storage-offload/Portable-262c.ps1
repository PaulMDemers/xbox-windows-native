#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws='C:\Users\Paul\Documents\Codex\2026-10-02\xbox-windows-feasibility'
$cache='C:\Users\Paul\AppData\Local\ogxbox-linux\instances'
$dest='E:\Codex-archive\xbox-windows-native\closed-portable-262c'
if(Test-Path -LiteralPath $dest){throw 'Never repeat completed or partial offload'}
New-Item -ItemType Directory -Path $dest | Out-Null
$all=@()
$plans=@(@{stem="coverage262";kit="surface-coverage262";case="emu001"})
foreach($plan in $plans){
 $case=$plan.case; $stem=$plan.stem; $kit=$plan.kit
 $run="E:\Codex-private-artifacts\xbox-windows-feasibility\$stem\runs\nt5-$stem-$case"
 $meta=Get-Content (Join-Path $run instance.json) -Raw | ConvertFrom-Json
 $state=Get-Content (Join-Path $ws "outputs/$kit/$case/host-state.json") -Raw | ConvertFrom-Json
 if(-not $state.closed -or -not $state.cleanup_record_exists){throw 'Owned controller still active'}
 if(-not (Test-Path -LiteralPath (Join-Path $run 'cleanup.json'))){throw 'Cleanup record required'}
 $task="windows-native-$stem"
 if($meta.taskId -ne $task -or (Get-Process -Name "xemu-$task" -ErrorAction SilentlyContinue)){throw 'Owned portable process identity still active'}
 $source=[IO.Path]::GetFullPath($meta.portableRoot)
 $expected=Join-Path (Join-Path $cache $task) $meta.sourceSha256.Substring(0,16)
 if($source -ne $expected -or -not $source.StartsWith($cache+'\') -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Exact intended portable boundary refused'}
 if(@(Get-ChildItem -LiteralPath $source -File -Recurse | Where-Object {$_.Extension -in '.qcow2','.iso','.img','.vhd'}).Count){throw 'Backing images not allowed'}
 if(@(Get-ChildItem -LiteralPath $source -Directory -Recurse | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Nested junction refused'}
 $items=@(Get-ChildItem -LiteralPath $source -File -Recurse)
 $rows=@($items | ForEach-Object {@{path=$_.FullName.Substring($source.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
 $target=Join-Path $dest $task;New-Item -ItemType Directory -Path $target | Out-Null
 foreach($entry in (Get-ChildItem -LiteralPath $source)){Copy-Item -LiteralPath $entry.FullName -Destination $target -Recurse}
 foreach($row in $rows){$p=Join-Path $target $row.path;if((Get-Item -LiteralPath $p).Length -ne $row.bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Copy mismatch; preserve source'}}
 if(@(Get-ChildItem -LiteralPath $target -File -Recurse).Count -ne $rows.Count){throw 'Inventory mismatch'}
 if([IO.Path]::GetFullPath($source) -ne $expected -or -not $source.StartsWith($cache+'\') -or (Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Resolved removal boundary changed'}
 Remove-Item -LiteralPath $source -Recurse
 New-Item -ItemType Junction -Path $source -Target $target | Out-Null
 foreach($row in $rows){if((Get-FileHash -LiteralPath (Join-Path $source $row.path)).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Original path readback mismatch'}}
 $all+=@{source=$source;target=$target;files=$rows;original_path_preserved=$true;disk_backing_chains_moved=$false;owned_vm_closed=$true}
}
@{closed=$true;entries=$all;free_c=(Get-PSDrive C).Free;free_e=(Get-PSDrive E).Free;physical_access=$false} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $ws 'outputs/task-storage-offload/portable-262c.json') -Encoding utf8
Write-Output 'Closed262 portable copy verified on E; original path retained'
