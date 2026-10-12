#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$source=Join-Path $ws 'outputs/xemu-cpu-surface-evict/build002/artifacts'
$target='D:\Codex-archive\xbox-windows-native\closed-artifacts-324'
$record=Join-Path $PSScriptRoot 'artifacts-324.json'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  if((Test-Path $record) -or (Test-Path $target)){throw 'Unique offload already exists'}
  if(Get-Process -Name xemu* -ErrorAction SilentlyContinue){throw 'Emulator active'}
  if((Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Already offloaded'}
  $files=@(Get-ChildItem -LiteralPath $source -File)
  if($files.Count -ne 2 -or @(Get-ChildItem -LiteralPath $source).Count -ne 2 -or @($files | Where-Object Extension -ne '.exe').Count){throw 'Only two closed build executables allowed'}
  $pins=@($files | ForEach-Object {@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})
  if((Get-PSDrive D).Free - ($files | Measure-Object Length -Sum).Sum -lt 20GB){throw 'Archive guard'}
  New-Item -ItemType Directory -Path $target | Out-Null
  foreach($p in $pins){Copy-Item -LiteralPath (Join-Path $source $p.name) -Destination (Join-Path $target $p.name)}
  foreach($p in $pins){if((Get-FileHash -LiteralPath (Join-Path $target $p.name)).Hash.ToLowerInvariant() -ne $p.sha256){throw 'Copy hash mismatch'}}
  $r=@{source=$source;target=$target;pins=$pins;backing_media_moved=$false;completed=$false}
  $r | ConvertTo-Json -Depth 8 | Set-Content $record
  $absolute=[IO.Path]::GetFullPath($source)
  if($absolute -ne (Join-Path $ws 'outputs\xemu-cpu-surface-evict\build002\artifacts') -or (Get-Item -LiteralPath $absolute).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Removal boundary mismatch'}
  foreach($p in $pins){if((Get-FileHash -LiteralPath (Join-Path $absolute $p.name)).Hash.ToLowerInvariant() -ne $p.sha256){throw 'Original changed'}}
  Remove-Item -LiteralPath $absolute -Recurse
  New-Item -ItemType Junction -Path $absolute -Target $target | Out-Null
  foreach($p in $pins){if((Get-FileHash -LiteralPath (Join-Path $absolute $p.name)).Hash.ToLowerInvariant() -ne $p.sha256){throw 'Original-path hash mismatch'}}
  $r.completed=$true;$r.free_c=(Get-PSDrive C).Free
  $r | ConvertTo-Json -Depth 8 | Set-Content $record
 }
}
