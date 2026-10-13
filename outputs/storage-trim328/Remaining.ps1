#requires -Version 7.4
param([Parameter(Mandatory)][int]$ArchivePid)
$ErrorActionPreference='Stop'
$receipt='E:/xwn328/remaining-start001.json'
if(Test-Path -LiteralPath $receipt){throw 'Consumed remaining attempt'}
@{utc=[DateTime]::UtcNow.ToString('o');archivePid=$ArchivePid;purpose='Wait for owned first pass, then run reviewed second pass and duplicate pruning'} | ConvertTo-Json | Set-Content -LiteralPath $receipt
$proc=Get-Process -Id $ArchivePid -ErrorAction SilentlyContinue
if($proc) {
 $deadline=[DateTime]::UtcNow.AddMinutes(45)
 while(-not $proc.WaitForExit(10000)) {if([DateTime]::UtcNow -gt $deadline){throw 'First pass exceeded bounded wait'}}
}
$rows=Get-Content -LiteralPath E:/xwn328/archive-journal001.jsonl | ForEach-Object {$_ | ConvertFrom-Json}
$done=@($rows | Where-Object source_removed | Select-Object -ExpandProperty source -Unique)
if($done.Count -ne 385){throw 'First archive pass incomplete; do not continue'}
& (Join-Path $PSScriptRoot Archive002.ps1)
& (Join-Path $PSScriptRoot Prune.ps1)
@{utc=[DateTime]::UtcNow.ToString('o');completed=$true} | ConvertTo-Json | Set-Content -LiteralPath E:/xwn328/remaining-complete001.json
