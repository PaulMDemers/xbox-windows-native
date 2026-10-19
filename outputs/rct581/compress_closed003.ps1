$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression003.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$targets=@()
foreach($n in @(373,377,389,392)){
 foreach($disk in Get-ChildItem -LiteralPath "C:\xwn$n\runs" -Filter hdd.qcow2 -Recurse -File){
  $state=Get-Content (Join-Path $disk.DirectoryName 'host-exit.json') -Raw | ConvertFrom-Json
  if(-not $state.closed){throw 'Process not closed'}
  $targets += $disk.FullName
 }
}
if($targets.Count -ne 4){throw 'Expected four closed disks'}
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;rows=@();scope='Lossless compression of four closed retained disks; no launch, deletion, chain move or content change. Full file scratch reserve.'}
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
foreach($target in $targets){
 $p=(Resolve-Path -LiteralPath $target).Path
 if($p -ne $target){throw 'Exact path mismatch'}
 $bytes=(Get-Item -LiteralPath $p).Length
 if((Get-PSDrive C).Free-$bytes -lt 20GB){throw 'Scratch guard failed'}
 $row=[ordered]@{path=$p;bytes=$bytes;sha256=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant();completed=$false}
 $r.rows += $row;$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
 & compact.exe /C /I /Q $p | Out-Null
 if($LASTEXITCODE -ne 0){throw 'Compression failed'}
 $row['after_sha256']=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant();$row.completed=$row.after_sha256 -eq $row.sha256
 if(-not $row.completed){throw 'Hash mismatch'}
 $r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
Write-Output ('Four disks preserved; free='+$r.after_free_bytes)
