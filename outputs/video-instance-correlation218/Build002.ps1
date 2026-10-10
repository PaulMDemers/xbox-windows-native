#requires -Version 7.4
$ErrorActionPreference='Stop'
if((Get-PSDrive C).Free -lt 20GB -or (Get-PSDrive E).Free -lt 20GB){throw '20GiB guard'}
$pins=Get-Content (Join-Path $PSScriptRoot build-inputs002.json) -Raw | ConvertFrom-Json
foreach($p in $pins.files.PSObject.Properties){if((Get-FileHash -LiteralPath $p.Name).Hash.ToLowerInvariant() -ne $p.Value){throw ('Changed input '+$p.Name)}}
$build='E:/Codex-build/xwninst218b'
$artifacts=Join-Path $PSScriptRoot artifacts/build002
if((Test-Path -LiteralPath $build) -or (Test-Path -LiteralPath $artifacts)){throw 'Unique build already exists'}
New-Item -ItemType Directory -Path $build,$artifacts | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot main002.c) -Destination (Join-Path $build main.c)
Copy-Item -LiteralPath (Join-Path $PSScriptRoot correlation.h),(Join-Path $PSScriptRoot Makefile),(Join-Path $PSScriptRoot test-correlation.c) -Destination $build
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Homebrew/Invoke-Console.ps1 -Console xbox -WorkingDirectory $build -Command 'make -j4' *> (Join-Path $artifacts build-console.txt)
 if($LASTEXITCODE -ne 0){throw '218 NXDK build failed; preserve build001'}

}
Copy-Item -LiteralPath (Join-Path $build main.exe),(Join-Path $build main.obj),(Join-Path $build bin/default.xbe),(Join-Path $build xwn-instance218.iso) -Destination $artifacts
foreach($p in $pins.files.PSObject.Properties){if((Get-FileHash -LiteralPath $p.Name).Hash.ToLowerInvariant() -ne $p.Value){throw ('Input/library changed during build '+$p.Name)}}
Get-ChildItem -LiteralPath $artifacts -File | Get-FileHash | ConvertTo-Json | Set-Content (Join-Path $PSScriptRoot build002-files.json)
