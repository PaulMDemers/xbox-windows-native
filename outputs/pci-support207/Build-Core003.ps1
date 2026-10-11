#requires -Version 7.4
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if((Get-Content -LiteralPath (Join-Path $repo '.git/HEAD') -Raw).Trim() -ne 'ref: refs/heads/codex/xbox-native-pci'){throw 'Branch guard'}
if((& git -C $repo remote get-url origin) -ne 'https://github.com/PaulMDemers/xbox-windows-native.git'){throw 'Origin guard'}
if((Get-PSDrive C).Free - 64MB -lt 20GB){throw '20GiB projected guard'}
$out=Join-Path $PSScriptRoot 'artifacts/core003'
if(Test-Path -LiteralPath $out){throw 'Fresh build ID required'}

$p='/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    New-Item -ItemType Directory -Path $out | Out-Null
    & wsl -d Ubuntu -- gcc -Wall -Wextra -Werror '-fsanitize=address,undefined' -g -o ($p+'/artifacts/core003/test-smbus') ($p+'/test-smbus.c')
    if($LASTEXITCODE){throw 'Host compile failed'}
    & wsl -d Ubuntu -- ($p+'/artifacts/core003/test-smbus') | Set-Content (Join-Path $PSScriptRoot 'core003-tests.json')
    if($LASTEXITCODE){throw 'Host tests failed'}
    & wsl -d Ubuntu -- gcc -Os -Wall -Wextra -Werror -o ($p+'/artifacts/core003/smbus-model-host') ($p+'/smbus-model.c')
    if($LASTEXITCODE){throw 'Model transport compile failed'}
}
@{scope='Host engine/transport only; no guest driver';physical_access=$false;files=@(Get-ChildItem -LiteralPath $out -File | ForEach-Object { @{name=$_.Name;sha256=(Get-FileHash $_.FullName).Hash.ToLowerInvariant()} });sources=@('smbus.h','test-smbus.c','smbus-model.c') | ForEach-Object { @{name=$_;sha256=(Get-FileHash (Join-Path $PSScriptRoot $_)).Hash.ToLowerInvariant()} }} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $PSScriptRoot 'core003-build.json')
