#requires -Version 7.4
param([ValidatePattern('^nt5-ntfs-shutdown-[0-9]+$')][string]$RunId)
$ErrorActionPreference='Stop'
if (!$RunId) { throw 'Supply a new nt5-ntfs-shutdown-NNN run id.' }
$disk=Join-Path $PSScriptRoot ../native-windows-nt5-kernel/artifacts/windows2000-integrated-001.qcow2
$iso=Join-Path $PSScriptRoot artifacts/ntfs-shutdown-002.iso
if ((Get-FileHash $disk).Hash -ne '640DA2CCFE86774DD512D846D9674F19D7E642C0DF008CA42952E97185E4445B') { throw 'NTFS fixture changed.' }
if ((Get-FileHash $iso).Hash -ne '5628AB18732E6ECA711032B3FCC30EC3B1F8849EB16CD40337CEE0AED9F5CDE0') { throw 'NTFS boot ISO changed.' }
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -AllowFramebufferFallback -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Emulator harness failed; inspect run logs.' }
