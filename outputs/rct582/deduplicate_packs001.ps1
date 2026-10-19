$ErrorActionPreference='Stop'
$receipt=Join-Path $PSScriptRoot 'pack-deduplication001.json'
if(Test-Path -LiteralPath $receipt){throw 'Receipt exists'}
$root=(Resolve-Path -LiteralPath 'C:\xwn401\reconstruct001').Path
$names=@('audio004','boot-e334','display303','fatx390','hd300')
$suffix='.git\objects\pack\pack-c5b66bb4d96991855142e9ade8a5ad3d9c6dedd4.pack'
$paths=@($names | ForEach-Object { (Resolve-Path -LiteralPath (Join-Path (Join-Path $root $_) $suffix)).Path })
$source=$paths[0];$hash=(Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant()
foreach($p in $paths){
 if(-not $p.StartsWith($root+'\',[StringComparison]::OrdinalIgnoreCase) -or (Get-Item -LiteralPath $p).Length -ne 100339474){throw 'Unexpected exact target'}
 if((Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $hash){throw 'Packs differ'}
 & git verify-pack ([IO.Path]::ChangeExtension($p,'.idx'))
 if($LASTEXITCODE -ne 0){throw 'Git pack integrity failed'}
}
$r=[ordered]@{completed=$false;before_free_bytes=(Get-PSDrive C).Free;retained_source=$source;sha256=$hash;rows=@();scope='Deduplicate five byte-identical immutable Git pack objects in retained401 source reconstructions using same-volume hard links. Every original pathname/content and index retained; no working-tree change, backing-chain move, runtime launch or proprietary payload removal.'}
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
foreach($p in $paths[1..4]){
 $tmp=$p+'.xwn582-link';if(Test-Path -LiteralPath $tmp){throw 'Temporary path exists'}
 if((Get-PSDrive C).Free-1MB -lt 20GB){throw 'Reserve failed'}
 $row=[ordered]@{path=$p;temporary=$tmp;linked=$false;verified=$false};$r.rows+=$row
 $r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
 New-Item -ItemType HardLink -Path $tmp -Value $source | Out-Null
 if((Get-FileHash -LiteralPath $tmp).Hash.ToLowerInvariant() -ne $hash){throw 'Temporary link differs'}
 Remove-Item -LiteralPath $p -Force
 Move-Item -LiteralPath $tmp -Destination $p
 $row.linked=$true
 if((Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant() -ne $hash){throw 'Final content differs'}
 & git verify-pack ([IO.Path]::ChangeExtension($p,'.idx'))
 if($LASTEXITCODE -ne 0){throw 'Final Git pack integrity failed'}
 $row.verified=$true;$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
}
if((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $hash){throw 'Retained source changed'}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 6 | Set-Content $receipt -Encoding utf8
Write-Output ('All original pack paths and bytes retained; free='+$r.after_free_bytes)
