$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'deduplicate-media007.json'
if(Test-Path -LiteralPath $receipt){throw 'Consumed ID'}
if((Get-Volume -DriveLetter C).FileSystem -ne 'NTFS'){throw 'Requires NTFS'}
$roots=@('C:\xwn403\input-media002','C:\xwn403\input-media003','C:\xwn404\media-structure001')
$groups=@{}
foreach($root in $roots){foreach($file in (Get-ChildItem -LiteralPath $root -Recurse -File -Filter '*.CAB')){
 $hash=(Get-FileHash -LiteralPath $file.FullName).Hash
 if(-not $groups.ContainsKey($hash)){$groups[$hash]=@()}
 $groups[$hash]+=$file.FullName
}}
$records=@()
foreach($hash in $groups.Keys){
 $members=$groups[$hash];$source=(Resolve-Path -LiteralPath $members[0]).Path
 foreach($name in @($members | Select-Object -Skip 1)){
  $target=(Resolve-Path -LiteralPath $name).Path
  if(-not ($target.StartsWith('C:\xwn403\input-media003\') -or $target.StartsWith('C:\xwn404\media-structure001\')) -or $target -eq $source){throw 'Unexpected target'}
  if((Get-FileHash -LiteralPath $target).Hash -ne $hash){throw 'Changed target'}
  $record=@{source=$source;target=$target;sha256=$hash.ToLower();bytes=(Get-Item -LiteralPath $target).Length;status='verified-before-replacement'}
  $records+=$record;$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
  Remove-Item -LiteralPath $target
  try {New-Item -ItemType HardLink -Path $target -Target $source | Out-Null}
  catch {Copy-Item -LiteralPath $source -Destination $target;throw}
  if((Get-FileHash -LiteralPath $target).Hash -ne $hash){throw 'Readback mismatch'}
  $record.status='immutable-media-hardlink-readback-verified';$records | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt
 }
}
@{files=$records.Count;logical_duplicate_bytes=($records | Measure-Object bytes -Sum).Sum;free_bytes=(Get-PSDrive C).Free} | ConvertTo-Json
