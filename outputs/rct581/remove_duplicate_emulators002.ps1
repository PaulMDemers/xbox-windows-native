$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'duplicate-emulator-cleanup002.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$base=Split-Path $PSScriptRoot
foreach($name in @('marker-capture468','busy-handoff471')){
 $final=Get-Content (Join-Path $base "$name/final-review.json") -Raw | ConvertFrom-Json
 if(-not $final.all_owned_emulators_closed){throw 'Owned processes not closed'}
}
foreach($name in @('nt5-marker466-emu002','nt5-marker466-emu003')){
 $final=Get-Content "C:\xwn466\runs\$name\host-exit.json" -Raw | ConvertFrom-Json
 if(-not $final.closed){throw '466 not closed'}
}
$prior=Get-Content (Join-Path $base 'rct579/host-compression005.json') -Raw | ConvertFrom-Json
if(-not $prior.completed){throw 'Missing exact prior inventory'}
$keep=$prior.rows[0]
$kept=(Resolve-Path -LiteralPath $keep.path).Path
if((Get-FileHash -LiteralPath $kept).Hash.ToLowerInvariant() -ne $keep.sha256){throw 'Retained identical copy differs'}
$selected=@($prior.rows | Where-Object { $_.path -ne $kept -and $_.path -match '^C:\\xwn(466|468|471)\\instances\\' })
if($selected.Count -ne 5){throw 'Expected five owned copies'}
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;retained_identical_copy=$kept;sha256=$keep.sha256;rows=@();scope='User-authorized old-build cleanup. Remove only five byte-identical inactive copied emulator executables; all disks, firmware, configs, traces, source/build manifests and remaining identical executable retained. No runtime launch/reparent.'}
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
foreach($item in $selected){
 $p=(Resolve-Path -LiteralPath $item.path).Path
 if($p -ne $item.path -or $p -notmatch '^C:\\xwn(466|468|471)\\instances\\[^\\]+\\EA3473314E6C0EA0\\xemu-[^\\]+\.exe$'){throw 'Exact owned target mismatch'}
 if(Get-Process -Name ([IO.Path]::GetFileNameWithoutExtension($p)) -ErrorAction SilentlyContinue){throw 'Executable active'}
 if((Get-Item -LiteralPath $p).Length -ne 191317057 -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $keep.sha256){throw 'Copy identity mismatch'}
 $row=[ordered]@{path=$p;bytes=$item.bytes;sha256=$keep.sha256;removed=$false};$r.rows+=$row
 $r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
 Remove-Item -LiteralPath $p
 $row.removed=-not(Test-Path -LiteralPath $p);if(-not $row.removed){throw 'Deletion not verified'}
 $r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
}
if((Get-FileHash -LiteralPath $kept).Hash.ToLowerInvariant() -ne $keep.sha256){throw 'Retained source changed'}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
Write-Output ('Five exact duplicate executable copies removed; free='+$r.after_free_bytes)
