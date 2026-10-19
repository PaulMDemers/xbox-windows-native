$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression002.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$base=Split-Path $PSScriptRoot
$f=Get-Content (Join-Path $base 'release-readiness403/emu001/fixture.json') -Raw | ConvertFrom-Json -AsHashtable
$c=Get-Content (Join-Path $base 'release-readiness403/emu001/closure.json') -Raw | ConvertFrom-Json -AsHashtable
$s=Get-Content (Join-Path $base 'marker-handoff466/preparation001.json') -Raw | ConvertFrom-Json -AsHashtable
if(-not $c.closed -or -not $s.seed_never_executed){throw 'Historical ownership failed'}
$rows=@(
 [ordered]@{path='C:\xwn403\install-restore002\boot-source.qcow2';sha256=$f.fixture_sha256},
 [ordered]@{path='C:\xwn403\install-restore002\restored.qcow2';sha256=$f.parent_sha256},
 [ordered]@{path='C:\xwn466\preparation001\seed.qcow2';sha256=$s.seed_sha256}
)
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;rows=$rows;scope='Lossless NTFS compression only; same exact paths and bytes; no historical boot/reparent/deletion. No host emulator was active at admission.'}
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
foreach($row in $rows){
 $target=(Resolve-Path -LiteralPath $row.path).Path
 if($target -ne $row.path){throw 'Exact path mismatch'}
 if((Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Historical hash mismatch'}
 $row['bytes']=(Get-Item -LiteralPath $target).Length
 if((Get-PSDrive C).Free-$row.bytes -lt 20GB){$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8;throw 'Compression scratch reserve refused'}
 & compact.exe /C /I /Q $target
 if($LASTEXITCODE -ne 0){throw 'Compression failed'}
 $row['after_sha256']=(Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant()
 $row['compressed']=[bool]((Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::Compressed)
 $row['completed']=$row.after_sha256 -eq $row.sha256 -and $row.compressed
 $r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
 if(-not $row.completed){throw 'Verification failed'}
}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
