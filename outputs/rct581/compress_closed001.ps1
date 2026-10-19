$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression001.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$rows=@();$kits=@(579,580,581)
foreach($n in $kits){
 $kit=Join-Path (Split-Path $PSScriptRoot) "rct$n"
 $final=Get-Content (Join-Path $kit 'final001.json') -Raw | ConvertFrom-Json -AsHashtable
 $state=Get-Content (Join-Path $kit 'ntfs-phase1.json') -Raw | ConvertFrom-Json -AsHashtable
 if(-not $final.closed -or -not $state.closed){throw 'Runtime not closed'}
 $root=(Resolve-Path -LiteralPath "C:\xwn$n\pc001").Path
 foreach($file in Get-ChildItem -LiteralPath $root -File -Recurse){
  if($file.Attributes -band [IO.FileAttributes]::Compressed){continue}
  if($file.Length -lt 65536 -or $file.Extension -eq '.qcow2'){continue}
  if(-not $file.FullName.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Scope mismatch'}
  $rows += [ordered]@{path=$file.FullName;bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash.ToLowerInvariant();completed=$false}
 }
}
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;rows=$rows;scope='Lossless NTFS compression of already closed private evidence; no guest/runtime access or deletion; hashes preserved'}
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
foreach($row in $rows){
 if((Get-PSDrive C).Free-$row.bytes -lt 20GB){throw 'Scratch guard failed'}
 & compact.exe /C /I /Q $row.path | Out-Null
 if($LASTEXITCODE -ne 0){throw 'Compression failed'}
 $row['after_sha256']=(Get-FileHash -LiteralPath $row.path).Hash.ToLowerInvariant()
 $row.completed=$row.after_sha256 -eq $row.sha256
 if(-not $row.completed){throw 'Hash verification failed'}
}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
Write-Output ('Verified '+$rows.Count+' retained files; free='+$r.after_free_bytes)
