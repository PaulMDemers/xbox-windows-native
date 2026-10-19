$ErrorActionPreference='Stop'
$out=Join-Path $PSScriptRoot 'transport578-cleanup001.json'
if(Test-Path -LiteralPath $out){throw 'Cleanup already recorded'}
$kit=Join-Path (Split-Path $PSScriptRoot) 'rct578'
$final=Get-Content (Join-Path $kit 'final001.json') -Raw | ConvertFrom-Json -AsHashtable
$runtime=Get-Content (Join-Path $kit 'ntfs-phase1.json') -Raw | ConvertFrom-Json -AsHashtable
$media=Get-Content (Join-Path $kit 'media001.json') -Raw | ConvertFrom-Json -AsHashtable
$build=Get-Content (Join-Path $kit 'runner-build001.json') -Raw | ConvertFrom-Json -AsHashtable
if(-not $final.closed -or -not $final.all_owned_processes_closed -or -not $runtime.closed){throw 'Runtime not closed'}
$target=(Resolve-Path -LiteralPath 'C:\xwn578\helper001.iso').Path
if($target -ne 'C:\xwn578\helper001.iso' -or $media.path -ne $target){throw 'Exact target mismatch'}
if((Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant() -ne $media.sha256){throw 'ISO hash mismatch'}
$exe='C:\xwn578\runner-build001\run578.exe'
if((Get-FileHash -LiteralPath $exe).Hash.ToLowerInvariant() -ne $build.rows[0].sha256){throw 'Retained runner mismatch'}
$package=Get-Content (Join-Path (Split-Path $PSScriptRoot) 'rct565/package001.json') -Raw | ConvertFrom-Json -AsHashtable
$checked=0
foreach($name in $package.files.Keys){
 if(-not $name.StartsWith('game/')){continue}
 $row=$package.files[$name]
 if((Get-FileHash -LiteralPath $row.path).Hash.ToLowerInvariant() -ne $row.sha256){throw 'Retained asset mismatch'}
 $checked++
}
if($checked -ne 502){throw 'Unexpected asset count'}
$r=[ordered]@{completed=$false;utc=[DateTime]::UtcNow.ToString('o');path=$target;sha256=$media.sha256;bytes=$media.bytes;retained_game_assets_verified=$checked;retained_runner_verified=$true;copy_script_retained_in_media_record=$true;before_free_bytes=(Get-PSDrive C).Free;scope='One redundant helper ISO after runtime closure; all assets, runner, manifests and closed guest disk retained; no guest reopen/reparent'}
$r | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $out -Encoding utf8
Remove-Item -LiteralPath $target
if(Test-Path -LiteralPath $target){throw 'Exact file still present'}
$r.completed=$true;$r['after_free_bytes']=(Get-PSDrive C).Free
$r | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $out -Encoding utf8
