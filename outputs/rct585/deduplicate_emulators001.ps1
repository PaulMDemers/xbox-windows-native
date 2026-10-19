$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'emulator-deduplication001.json'
if(Test-Path -LiteralPath $receipt){throw 'Evidence exists'}
$kept='C:\xwn466\instances\windows-native-marker466-emu001\EA3473314E6C0EA0\xemu-windows-native-marker466-emu001.exe'
$hash='ea3473314e6c0ea068de4202cde46b1405da7553240cadea738c29c16d74c7a3'
if((Resolve-Path -LiteralPath $kept).Path -ne $kept -or (Get-FileHash -LiteralPath $kept).Hash.ToLowerInvariant() -ne $hash){throw 'Retained copy differs'}
$rows=@()
foreach($n in @(371,373,377,389,392,393,403,502,505,507,511,512,513,517)){
 $root="C:\xwn$n"
 $states=@(Get-ChildItem -LiteralPath "$root\runs" -Filter host-exit.json -File -Recurse)
 $expected=if($n -eq 371){2}else{1}
 if($states.Count -ne $expected){throw 'Unexpected closure inventory'}
 foreach($state in $states){if(-not (Get-Content -LiteralPath $state.FullName -Raw|ConvertFrom-Json).closed){throw 'Runtime not closed'}}
 $files=@(Get-ChildItem -LiteralPath "$root\instances" -Filter '*.exe' -File -Recurse)
 if($files.Count -ne $expected){throw 'Unexpected executable inventory'}
 foreach($file in $files){
  $p=(Resolve-Path -LiteralPath $file.FullName).Path
  if(-not $p.StartsWith($root+'\instances\') -or $p -notmatch '\\EA3473314E6C0EA0\\xemu-[^\\]+\.exe$'){throw 'Owned path mismatch'}
  if(Get-Process -Name $file.BaseName -ErrorAction SilentlyContinue){throw 'Executable active'}
  if($file.Length -ne 191317057 -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $hash){throw 'Different bytes'}
  if(Test-Path -LiteralPath ($p+'.dedup585')){throw 'Temporary path exists'}
  $rows+=,[ordered]@{path=$p;bytes=$file.Length;sha256=$hash;old_last_write_utc=$file.LastWriteTimeUtc.ToString('o');closure=@($states|ForEach-Object{[ordered]@{path=$_.FullName;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}});renamed=$false;linked=$false;duplicate_removed=$false}
 }
}
if($rows.Count -ne 15){throw 'Expected fifteen copies'}
$r=[ordered]@{completed=$false;utc=[DateTime]::UtcNow.ToString('o');before_free_bytes=(Get-PSDrive C).Free;retained=$kept;sha256=$hash;rows=$rows;scope='User-authorized duplicate old-build cleanup. Same-volume hard links retain every executable path and exact contents. All closed disks, firmware, configs, logs and source preserved; no runtime reopened. Original file timestamps recorded; shared inode now uses retained copy metadata.'}
function Save-Receipt {$r|ConvertTo-Json -Depth 8|Set-Content -LiteralPath $receipt -Encoding utf8}
Save-Receipt
foreach($row in $rows){
 $p=$row.path;$tmp=$p+'.dedup585'
 if((Resolve-Path -LiteralPath $p).Path -ne $p -or (Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $hash){throw 'Changed target'}
 if(Get-Process -Name ([IO.Path]::GetFileNameWithoutExtension($p)) -ErrorAction SilentlyContinue){throw 'Executable became active'}
 Move-Item -LiteralPath $p -Destination $tmp;$row.renamed=$true;Save-Receipt
 try{New-Item -ItemType HardLink -Path $p -Target $kept|Out-Null;$row.linked=$true;Save-Receipt}
 catch{Move-Item -LiteralPath $tmp -Destination $p;throw}
 if((Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $hash -or (Get-Item -LiteralPath $p).LinkType -ne 'HardLink'){throw 'New link verification failed'}
 if((Resolve-Path -LiteralPath $tmp).Path -ne $tmp -or (Get-FileHash -LiteralPath $tmp).Hash.ToLowerInvariant() -ne $hash){throw 'Duplicate path verification failed'}
 Remove-Item -LiteralPath $tmp;$row.duplicate_removed=-not(Test-Path -LiteralPath $tmp);Save-Receipt
 if(-not $row.duplicate_removed){throw 'Duplicate remains'}
}
if((Get-FileHash -LiteralPath $kept).Hash.ToLowerInvariant() -ne $hash){throw 'Retained bytes changed'}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free;Save-Receipt
Write-Output ('Fifteen identical copies share retained bytes; free='+$r.after_free_bytes)
