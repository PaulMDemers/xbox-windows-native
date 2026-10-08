#requires -Version 7.4
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$build=Join-Path $ws 'work/gpu-swizzle153-build001'
if(Test-Path (Join-Path $PSScriptRoot 'build.json')){throw 'Build already recorded'}
if((Get-PSDrive C).Free -lt 20GB){throw '20 GiB build guard'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    & C:/Homebrew/Invoke-Console.ps1 -Console xbox -WorkingDirectory $build -Command 'make -j4'
    if($LASTEXITCODE -ne 0){throw 'Coherence build failed; preserve attempt'}
}
$inputs=Get-Content (Join-Path $PSScriptRoot 'build-inputs.json') -Raw | ConvertFrom-Json
foreach($item in $inputs.sdk_inputs){if((Get-FileHash -LiteralPath $item.path).Hash.ToLowerInvariant() -ne $item.sha256){throw 'Shared SDK input changed'}}
$art=Join-Path $PSScriptRoot 'artifacts'
New-Item -ItemType Directory -Path $art | Out-Null
Copy-Item -LiteralPath (Join-Path $build 'bin/default.xbe'),(Join-Path $build 'swizzle153.iso'),(Join-Path $build 'main.exe'),(Join-Path $build 'vs.inl'),(Join-Path $build 'ps.inl') -Destination $art
@{utc=[DateTime]::UtcNow.ToString('o');passed=$true;shared_sdk_unchanged=$true;inputs_sha256=(Get-FileHash (Join-Path $PSScriptRoot 'build-inputs.json')).Hash.ToLowerInvariant();files=@(Get-ChildItem $art | ForEach-Object {@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()}})} | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $PSScriptRoot 'build.json')
