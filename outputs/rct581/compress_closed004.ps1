$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression004.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$final=Get-Content (Join-Path $PSScriptRoot 'final001.json') -Raw | ConvertFrom-Json
if(-not $final.closed){throw 'Not closed'}
$p=(Resolve-Path -LiteralPath 'C:\xwn581\pc001\disk.qcow2').Path
if($p -ne 'C:\xwn581\pc001\disk.qcow2'){throw 'Exact path mismatch'}
$expected='0005d343f64784d372f73fe896e66beff52295c32a4f34ba4d60145f1f9c3d1b'
$bytes=(Get-Item -LiteralPath $p).Length
if((Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $expected){throw 'Hash mismatch'}
if((Get-PSDrive C).Free-$bytes -lt 20GB){throw 'Scratch guard failed'}
$r=[ordered]@{completed=$false;path=$p;sha256=$expected;bytes=$bytes;before_free_bytes=(Get-PSDrive C).Free;scope='Closed581 disk lossless compression; exact bytes and backing path retained; no launch/reparent/deletion'}
$r | ConvertTo-Json | Set-Content $receipt -Encoding utf8
& compact.exe /C /I /Q $p
if($LASTEXITCODE -ne 0){throw 'Compression failed'}
$r['after_sha256']=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant();$r.completed=$r.after_sha256 -eq $expected;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json | Set-Content $receipt -Encoding utf8
if(-not $r.completed){throw 'Verification failed'}
