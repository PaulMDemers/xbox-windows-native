$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression002.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$targets=@()
foreach($n in @(579,580)){
 $final=Get-Content (Join-Path (Split-Path $PSScriptRoot) "rct$n/final001.json") -Raw | ConvertFrom-Json
 $state=Get-Content (Join-Path (Split-Path $PSScriptRoot) "rct$n/ntfs-phase1.json") -Raw | ConvertFrom-Json
 if(-not $final.closed -or -not $state.closed){throw 'Not closed'}
 $targets += "C:\xwn$n\pc001\disk.qcow2"
}
$review=Get-Content (Join-Path (Split-Path $PSScriptRoot) 'stretch-runtime371/final-review.json') -Raw | ConvertFrom-Json
if(-not $review.all_owned_runs_closed){throw '371 not closed'}
foreach($case in @('control001','candidate001')){
 $folder="C:\xwn371\runs\nt5-stretch371-$case"
 $state=Get-Content "$folder\host-exit.json" -Raw | ConvertFrom-Json
 if(-not $state.closed){throw '371 process not closed'}
 $targets += "$folder\hdd.qcow2"
}
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
