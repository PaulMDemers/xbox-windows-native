$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression001.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$rows=@()
foreach($n in @(569,570)){
    $kit=Join-Path (Split-Path $PSScriptRoot) "rct$n"
    $final=Get-Content (Join-Path $kit 'final001.json') -Raw | ConvertFrom-Json -AsHashtable
    $state=Get-Content (Join-Path $kit 'ntfs-phase1.json') -Raw | ConvertFrom-Json -AsHashtable
    $cold=Get-Content (Join-Path $kit 'ntfs-cold1-002.json') -Raw | ConvertFrom-Json -AsHashtable
    if(-not $final.closed -or -not $state.closed -or -not $cold.complete -or $state.disk_sha256 -ne $cold.disk_sha256){throw 'Control not closed and pinned'}
    $target=(Resolve-Path -LiteralPath "C:\xwn$n\pc001\disk.qcow2").Path
    if($target -ne "C:\xwn$n\pc001\disk.qcow2"){throw 'Unexpected exact path'}
    $hash=(Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant()
    if($hash -ne $state.disk_sha256){throw 'Disk pin mismatch'}
    if((Get-PSDrive C).Free-(Get-Item -LiteralPath $target).Length -lt 20GB){throw 'Conservative compression scratch reserve failed'}
    $rows += [ordered]@{path=$target;sha256=$hash;bytes=(Get-Item -LiteralPath $target).Length;completed=$false}
}
$r=[ordered]@{completed=$false;beforeFreeBytes=(Get-PSDrive C).Free;rows=$rows;scope='NTFS compression only of closed569/570 containers; no guest reopen, reparent, deletion or byte change'}
$r | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
foreach($row in $rows){
    & compact.exe /C /I /Q $row.path
    if($LASTEXITCODE -ne 0){throw 'Compression failed; receipt retained'}
    $row['after_sha256']=(Get-FileHash -LiteralPath $row.path).Hash.ToLowerInvariant()
    $row['compressed']=[bool]((Get-Item -LiteralPath $row.path).Attributes -band [IO.FileAttributes]::Compressed)
    $row.completed=$row.after_sha256 -eq $row.sha256 -and $row.compressed
    $r | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
    if(-not $row.completed){throw 'Compression verification failed'}
}
$r.completed=$true
$r['afterFreeBytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $receipt -Encoding utf8
