$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression006.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$rows=@()
foreach($n in @(371,373,377,389,392,393,403)){
 foreach($run in Get-ChildItem -LiteralPath "C:\xwn$n\runs" -Directory){
  if(-not (Test-Path -LiteralPath (Join-Path $run.FullName 'host-exit.json'))){continue}
  $state=Get-Content (Join-Path $run.FullName 'host-exit.json') -Raw | ConvertFrom-Json
  if(-not $state.closed){continue}
  $root=$run.FullName
  foreach($file in Get-ChildItem -LiteralPath $root -File -Recurse){
   if($file.Attributes -band [IO.FileAttributes]::Compressed){continue}
   if($file.Length -lt 65536 -or $file.Extension -eq '.qcow2'){continue}
   if(-not $file.FullName.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Scope mismatch'}
   $rows += [ordered]@{path=$file.FullName;bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash.ToLowerInvariant();completed=$false}
  }
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
