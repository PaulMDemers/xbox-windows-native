$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'deduplicate-c002.json'
if(Test-Path -LiteralPath $receipt){throw 'Consumed ID'}
if((Get-Volume -DriveLetter C).FileSystem -ne 'NTFS'){throw 'Requires NTFS'}
if(Get-Process xemu*,git -ErrorAction SilentlyContinue){throw 'Owned binaries/repos may be active'}
$roots=@('C:\xwn371\instances','C:\xwn373\instances','C:\xwn377\instances','C:\xwn389\instances','C:\xwn392\instances','C:\xwn393\instances','C:\xwn403\instances')
$files=@(foreach($root in $roots){Get-ChildItem -LiteralPath $root -Recurse -File -Filter 'xemu*.exe'})
$files+=@(Get-ChildItem -LiteralPath 'C:\xwn401\reconstruct001' -Recurse -File -Filter 'pack-c5b66bb4d96991855142e9ade8a5ad3d9c6dedd4.pack')
$groups=@{}
foreach($file in $files){
 if($file.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse file'}
 $hash=(Get-FileHash -LiteralPath $file.FullName).Hash
 if(-not $groups.ContainsKey($hash)){$groups[$hash]=@()}
 $groups[$hash]+=$file.FullName
}
$records=@()
foreach($hash in $groups.Keys){
 $members=$groups[$hash];$source=(Resolve-Path -LiteralPath $members[0]).Path
 foreach($name in @($members | Select-Object -Skip 1)){
  $target=(Resolve-Path -LiteralPath $name).Path
  if(-not ($target -match '^C:\\xwn(371|373|377|389|392|393|401|403)\\') -or $target -eq $source){throw 'Unexpected target'}
  $length=(Get-Item -LiteralPath $target).Length
  if((Get-FileHash -LiteralPath $target).Hash -ne $hash){throw 'Changed target'}
  $record=@{source=$source;target=$target;sha256=$hash.ToLower();bytes=$length;status='verified-before-replacement'}
  $records+=$record;$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
  Remove-Item -LiteralPath $target
  try { New-Item -ItemType HardLink -Path $target -Target $source | Out-Null }
  catch { Copy-Item -LiteralPath $source -Destination $target; $record.status='failure-copy-restored';$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt;throw }
  if((Get-FileHash -LiteralPath $target).Hash -ne $hash){throw 'Readback failed'}
  $record.status='hardlink-readback-verified';$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
 }
}
@{files=$records.Count;logical_duplicate_bytes=($records | Measure-Object bytes -Sum).Sum;free_bytes=(Get-PSDrive C).Free;scope='Immutable closed emulator executables and identical Git object packs only; all original paths/bytes retained. Break links before any future in-place binary rewrite.'} | ConvertTo-Json
