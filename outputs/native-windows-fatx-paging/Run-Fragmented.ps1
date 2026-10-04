#requires -Version 7.4
param([ValidatePattern('^nt5-fatx-boot-paging-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
if (!$RunId) { throw 'Supply a new nt5-fatx-boot-paging-NNN run id.' }
$disk=Join-Path $PSScriptRoot artifacts/windows2000-fatx-fragmented-paging-001.qcow2
$iso=Join-Path $PSScriptRoot ../native-windows-fatx-boot/artifacts/fatx-boot-001.iso
if ((Get-FileHash $disk).Hash -ne '6D2899FA61A1F7E640096F80E8159CF6B32A96C4C4BD7BC5732F04B718803B57') { throw 'FATX fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '8AF80464D11FE100C1042D223A914D0AB0314E9C85D8D78E338DD1E7D70A04ED') { throw 'FATX boot ISO changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -UsbMouse -LaunchXromwell -Autorun -RetainDisk -StopOnBugcheck -StopOnCaptureComplete -Seconds 300
if ($LASTEXITCODE) { throw 'Emulator harness failed; inspect run logs.' }
