$ErrorActionPreference='Stop'
$recordPath=Join-Path $PSScriptRoot 'transport-cleanup001.json'
if(Test-Path -LiteralPath $recordPath){throw 'Cleanup already recorded'}
$final=Get-Content (Join-Path $PSScriptRoot 'final001.json') -Raw | ConvertFrom-Json -AsHashtable
$media=Get-Content (Join-Path $PSScriptRoot 'media001.json') -Raw | ConvertFrom-Json -AsHashtable
if(-not $final.closed){throw 'Control not closed'}
if(@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' -or $_.Name -like 'qemu-system*' }).Count){throw 'Emulator active'}
$target=(Resolve-Path -LiteralPath 'C:\xwn569\helper001.iso').Path
if($target -ne 'C:\xwn569\helper001.iso' -or $target -ne $media.path){throw 'Unexpected transport path'}
$hash=(Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant()
if($hash -ne $media.sha256){throw 'Transport pin mismatch'}
$record=[ordered]@{completed=$false; path=$target; bytes=(Get-Item -LiteralPath $target).Length; sha256=$hash; beforeFreeBytes=(Get-PSDrive C).Free; scope='Only reproducible owned transport ISO; original retail media, disk, logs, captures and exported files retained'}
$record | ConvertTo-Json | Set-Content -LiteralPath $recordPath -Encoding utf8
Remove-Item -LiteralPath $target
$record.completed= -not (Test-Path -LiteralPath $target)
$record['afterFreeBytes']=(Get-PSDrive C).Free
$record | ConvertTo-Json | Set-Content -LiteralPath $recordPath -Encoding utf8
if(-not $record.completed){throw 'Transport remains'}
