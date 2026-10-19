$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'closed-disk-compression001.json'
if(Test-Path -LiteralPath $receipt){throw 'Evidence exists'}
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;rows=@();scope='Lossless NTFS compression of closed582/584 disks, preserving exact contents and backing paths. No guest reopen/reparent. Whole-file scratch reserve.'}
$base=Split-Path $PSScriptRoot
foreach($n in @(582,584)){
 $final=Get-Content (Join-Path $base "rct$n/final001.json") -Raw|ConvertFrom-Json
 $runtime=Get-Content (Join-Path $base "rct$n/ntfs-phase1.json") -Raw|ConvertFrom-Json
 if(-not $final.closed -or -not $runtime.closed){throw 'Runtime still open'}
 $p="C:\xwn$n\pc001\disk.qcow2"
 if((Resolve-Path -LiteralPath $p).Path -ne $p){throw 'Path mismatch'}
 $bytes=(Get-Item -LiteralPath $p).Length
 if((Get-PSDrive C).Free-$bytes -lt 20GB){throw 'Scratch guard'}
 $hash=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant()
 if($hash -ne $runtime.disk_sha256 -or $hash -ne $final.disk_sha256){throw 'Closed disk mismatch'}
 $row=[ordered]@{path=$p;bytes=$bytes;sha256=$hash;completed=$false};$r.rows+=$row
 $r|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $receipt -Encoding utf8
 & compact.exe /C /I /Q $p|Out-Null
 if($LASTEXITCODE -ne 0){throw 'Compression failed'}
 $row['after_sha256']=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant()
 if($row.after_sha256 -ne $hash){throw 'Content changed'}
 $row.completed=$true;$r|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $receipt -Encoding utf8
}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r|ConvertTo-Json -Depth 6|Set-Content -LiteralPath $receipt -Encoding utf8
Write-Output ('Closed disks preserved; free='+$r.after_free_bytes)
