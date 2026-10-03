#requires -Version 7.4
$ErrorActionPreference='Stop'
$source=$PSScriptRoot
$workspace=Split-Path -Parent (Split-Path -Parent $source)
$build=Join-Path $workspace 'work/hardware-probe-v2-build'
New-Item -ItemType Directory -Force -Path $build | Out-Null
Copy-Item -LiteralPath (Join-Path $source 'main.c'),(Join-Path $source 'Makefile'),(Join-Path $source 'pci-policy.h') -Destination $build
& 'C:\Users\Paul\Desktop\ogxbox-linux\scripts\with_xbox_resource.ps1' -Resource build -Action {
    & C:\Homebrew\Invoke-Console.ps1 -Console xbox -WorkingDirectory $build -Command 'make -j4'
    if ($LASTEXITCODE -ne 0) { throw 'Hardware probe build failed' }
}
New-Item -ItemType Directory -Force -Path (Join-Path $source 'artifacts') | Out-Null
Copy-Item -LiteralPath (Join-Path $build 'bin/default.xbe'),(Join-Path $build 'xwn-hardware-probe.iso') -Destination (Join-Path $source 'artifacts')
