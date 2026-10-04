#requires -Version 7.4
param([ValidatePattern('^nt5-fatx-boot-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
if (!$RunId) { throw 'Supply a new nt5-fatx-boot-NNN run id.' }
$disk=Join-Path $PSScriptRoot ../native-windows-fatx-runtime/artifacts/windows2000-fatx-boot-001.qcow2
$iso=Join-Path $PSScriptRoot artifacts/fatx-boot-001.iso
if ((Get-FileHash $disk).Hash -ne '7679CA11D28B3B1E40AA93F3B0609E31A22CE26DDE08FC45FF169E33D5A31Cfd') { throw 'FATX fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '8AF80464D11FE100C1042D223A914D0AB0314E9C85D8D78E338DD1E7D70A04ED') { throw 'FATX boot ISO changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -UsbMouse -LaunchXromwell -Autorun -RetainDisk -Seconds 180
if ($LASTEXITCODE) { throw 'Emulator harness failed; inspect run logs.' }
