$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$root=(Resolve-Path (Join-Path $repo 'outputs')).Path+'\'
$receipt=Join-Path $PSScriptRoot 'record-compression001.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$changed=@(& git -C $repo diff --name-only -- outputs)
if($LASTEXITCODE -ne 0 -or $changed.Count){throw 'Tracked outputs have edits'}
$rows=@()
foreach($relative in @(& git -C $repo ls-files outputs)){
 $p=(Resolve-Path -LiteralPath (Join-Path $repo $relative)).Path
 if(-not $p.StartsWith($root,[StringComparison]::OrdinalIgnoreCase)){throw 'Path escaped outputs'}
 $f=Get-Item -LiteralPath $p
 if($f.Length -le 32KB -or ($f.Attributes -band [IO.FileAttributes]::Compressed)){continue}
 if($f.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Unexpected reparse point'}
 if($f.Extension -notin @('.json','.txt','.md','.py','.c','.h','.log','.csv')){continue}
 $rows+=,[ordered]@{path=$relative;bytes=$f.Length;sha256=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant();verified=$false}
}
$r=[ordered]@{completed=$false;started_utc=[DateTime]::UtcNow.ToString('o');before_free_bytes=(Get-PSDrive C).Free;scope='Lossless NTFS compression of tracked public text records; exact paths and bytes preserved. No deletion, disk reopen, backing move or guest change.';rows=$rows}
function Save-Record {$r|ConvertTo-Json -Depth 7|Set-Content -LiteralPath $receipt -Encoding utf8}
Save-Record
for($i=0;$i -lt $rows.Count;$i+=24){
 $batch=@($rows[$i..([Math]::Min($i+23,$rows.Count-1))]);$bytes=($batch|Measure-Object bytes -Sum).Sum
 if((Get-PSDrive C).Free-$bytes-8MB -lt 20GB){throw 'Projected whole-batch scratch reserve failed'}
 $paths=@($batch|ForEach-Object{Join-Path $repo $_.path})
 & compact.exe /C /I /Q @paths|Out-Null
 if($LASTEXITCODE -ne 0){throw 'Compression command failed'}
 foreach($row in $batch){
  $p=Join-Path $repo $row.path
  $after=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant()
  if($after -ne $row.sha256){throw 'Text bytes changed'}
  $row.verified=$true
 }
 Save-Record
}
$r.completed=$true;$r['ended_utc']=[DateTime]::UtcNow.ToString('o');$r['after_free_bytes']=(Get-PSDrive C).Free;Save-Record
Write-Output ('Verified compressed text files: '+$rows.Count+'; free='+$r.after_free_bytes)
