$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression004.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$pkg=Get-Content (Join-Path (Split-Path $PSScriptRoot) 'rct565/package001.json') -Raw | ConvertFrom-Json -AsHashtable
$root=(Resolve-Path -LiteralPath 'C:\xwn566\transfer002\game').Path
$rows=@()
foreach($entry in $pkg.files.GetEnumerator()){
 if(-not $entry.Key.StartsWith('game/')){continue}
 $p=(Resolve-Path -LiteralPath $entry.Value.path).Path
 if(-not $p.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Asset path scope mismatch'}
 $item=Get-Item -LiteralPath $p
 if($item.Length -ne $entry.Value.bytes -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $entry.Value.sha256){throw 'Retail asset pin mismatch'}
 $rows += [ordered]@{path=$p;bytes=$item.Length;sha256=$entry.Value.sha256;completed=$false}
}
if($rows.Count -ne 502){throw 'Unexpected asset count'}
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;rows=$rows;scope='Lossless NTFS compression of verified private retail assets; no game execution, binary mutation or deletion'}
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
foreach($row in $rows){
 if((Get-PSDrive C).Free-$row.bytes -lt 20GB){throw 'Scratch reserve failed'}
 & compact.exe /C /I /Q $row.path | Out-Null
 if($LASTEXITCODE -ne 0){throw 'Compression failed'}
 $row['after_sha256']=(Get-FileHash -LiteralPath $row.path).Hash.ToLowerInvariant();$row.completed=$row.after_sha256 -eq $row.sha256
 if(-not $row.completed){throw 'Verification failed'}
}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
Write-Output ('Verified '+$rows.Count+' assets; free='+$r.after_free_bytes)
