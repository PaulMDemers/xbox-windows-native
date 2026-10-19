$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'host-compression005.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$rows=@()
foreach($n in @(466,468,471,524,527,528)){
 $root=(Resolve-Path -LiteralPath "C:\xwn$n\instances").Path
 foreach($item in Get-ChildItem -LiteralPath $root -File -Filter 'xemu-*.exe' -Recurse){
  if(-not $item.FullName.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase) -or $item.Length -ne 191317057){throw 'Unexpected copied emulator'}
  if(Get-Process -Name $item.BaseName -ErrorAction SilentlyContinue){throw 'Emulator active'}
  $rows += [ordered]@{path=$item.FullName;bytes=$item.Length;sha256=(Get-FileHash -LiteralPath $item.FullName).Hash.ToLowerInvariant();completed=$false}
 }
}
if($rows.Count -ne 11 -or @($rows.sha256 | Select-Object -Unique).Count -ne 1){throw 'Expected identical retained emulator copies'}
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;rows=$rows;scope='Lossless NTFS compression of eleven identical inactive owned emulator executable copies. No launch, deletion or runtime access. Exact bytes and paths preserved.'}
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
foreach($row in $rows){
 if((Get-PSDrive C).Free-$row.bytes -lt 20GB){throw 'Scratch guard failed'}
 & compact.exe /C /I /Q $row.path | Out-Null
 if($LASTEXITCODE -ne 0){throw 'Compression failed'}
 $row['after_sha256']=(Get-FileHash -LiteralPath $row.path).Hash.ToLowerInvariant();$row.completed=$row.after_sha256 -eq $row.sha256
 if(-not $row.completed){throw 'Verification failed'}
}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
Write-Output ('Verified '+$rows.Count+' emulator copies; free='+$r.after_free_bytes)
