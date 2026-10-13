#requires -Version 7.4
$ErrorActionPreference='Stop'
$root='E:\Codex-archive\xbox-windows-native'
$journal='E:/xwn328/prune-journal001.jsonl'
if(Test-Path -LiteralPath $journal){throw 'Consumed prune attempt'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  if(@(Get-Process xemu*,qemu-system* -ErrorAction SilentlyContinue).Count){throw 'Emulator running'}
  $rows=Get-Content -LiteralPath E:/xwn328/dedup-plan001.json -Raw | ConvertFrom-Json
  foreach($row in $rows) {
   $target=[IO.Path]::GetFullPath($row.target);$keep=[IO.Path]::GetFullPath($row.canonical)
   if(-not $target.StartsWith($root+'\closed-portable',[StringComparison]::OrdinalIgnoreCase) -or
      -not $keep.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase) -or $target -eq $keep){throw 'Path refused'}
   foreach($p in @($target,$keep)) {
    $item=Get-Item -LiteralPath $p
    if($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $item.Length -ne $row.bytes){throw 'Changed file'}
    if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Hash mismatch'}
   }
   $proof=[ordered]@{target=$target;canonical=$keep;sha256=$row.sha256;bytes=$row.bytes;reason='Byte-identical executable in closed portable copy; canonical retained';removed=$false}
   $proof | ConvertTo-Json | Set-Content -LiteralPath ($target+'.deduplicated328.json')
   Remove-Item -LiteralPath $target
   $proof.removed=$true
   $proof | ConvertTo-Json | Set-Content -LiteralPath ($target+'.deduplicated328.json')
   $proof | ConvertTo-Json -Compress | Add-Content -LiteralPath $journal
  }
  $tools=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../work/microsoft-dump-reader'))
  $prov=Get-Content -LiteralPath (Join-Path $tools provenance.json) -Raw | ConvertFrom-Json
  foreach($entry in $prov.files.PSObject.Properties) {
   $p=[IO.Path]::GetFullPath((Join-Path $tools $entry.Name))
   if(-not $p.StartsWith($tools+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Provider path outside tools'}
   if((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.Value){throw 'Extracted debugger changed'}
  }
  foreach($leaf in @('windbg.msixbundle','windbg_win-x64.msix')) {
   $p=[IO.Path]::GetFullPath((Join-Path $tools $leaf))
   if(-not $p.StartsWith($tools+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Installer path refused'}
   $proof=[ordered]@{target=$p;sha256=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant();bytes=(Get-Item -LiteralPath $p).Length;reason='Downloaded installer; all extracted debugger providers rehashed against retained provenance';removed=$false}
   $proof | ConvertTo-Json | Set-Content -LiteralPath ($p+'.pruned328.json')
   Remove-Item -LiteralPath $p
   $proof.removed=$true;$proof | ConvertTo-Json | Set-Content -LiteralPath ($p+'.pruned328.json')
   $proof | ConvertTo-Json -Compress | Add-Content -LiteralPath $journal
  }
 }
}
