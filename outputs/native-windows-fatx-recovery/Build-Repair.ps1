#requires -Version 7.4
$ErrorActionPreference='Stop'
$source=$PSScriptRoot
$workspace=Split-Path -Parent (Split-Path -Parent $source)
$build=Join-Path $workspace 'work/fatx-repair-build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
Copy-Item -LiteralPath (Join-Path $source 'Makefile') -Destination $build
Copy-Item -LiteralPath (Join-Path $source 'repair.c') -Destination (Join-Path $build 'main.c')
& 'C:\Users\Paul\Desktop\ogxbox-linux\scripts\with_xbox_resource.ps1' -Resource build -Action {
    & C:\Homebrew\Invoke-Console.ps1 -Console xbox -WorkingDirectory $build -Command 'make -j4'
    if ($LASTEXITCODE -ne 0) { throw 'Hardware probe build failed' }
}
New-Item -ItemType Directory -Force -Path (Join-Path $source 'artifacts') | Out-Null
Copy-Item -LiteralPath (Join-Path $build 'bin/default.xbe') -Destination (Join-Path $source 'artifacts/repair.xbe')
