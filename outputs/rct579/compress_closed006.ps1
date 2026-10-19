$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression006.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$p=(Resolve-Path -LiteralPath 'C:\xwn466\preparation001\seed.qcow2').Path
if($p -ne 'C:\xwn466\preparation001\seed.qcow2'){throw 'Exact path mismatch'}
$expected='7709d6ac9867cb842c2f95f3478fced69f106fad5d199abebf004d464c4c2670'
$bytes=(Get-Item -LiteralPath $p).Length
if((Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $expected){throw 'Hash mismatch'}
if((Get-PSDrive C).Free-$bytes -lt 20GB){throw 'Scratch guard failed'}
$r=[ordered]@{completed=$false;path=$p;sha256=$expected;bytes=$bytes;before_free_bytes=(Get-PSDrive C).Free;scope='Previously refused immutable never-executed seed compression after capacity recovered; source pin unchanged; no launch/reparent/deletion'}
$r | ConvertTo-Json | Set-Content $receipt -Encoding utf8
& compact.exe /C /I /Q $p
if($LASTEXITCODE -ne 0){throw 'Compression failed'}
$r['after_sha256']=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant();$r.completed=$r.after_sha256 -eq $expected;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json | Set-Content $receipt -Encoding utf8
if(-not $r.completed){throw 'Verification failed'}
