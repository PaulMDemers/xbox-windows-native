#requires -Version 7.4
param(
 [Parameter(Mandatory)][ValidatePattern('^nt5-fatx-boot-persistence-[0-9]+$')][string]$RunId,
 [ValidatePattern('^nt5-fatx-boot-persistence-[0-9]+$')][string]$SourceRun,
 [switch]$Wide
)
$ErrorActionPreference='Stop'
$disk=Join-Path $PSScriptRoot artifacts/windows2000-fatx-persistence-001.qcow2
$expected='D7A0838D781D063660F61EED02D5B7A7549811684B9AD6D66814E17E9155DDE5'
if ($SourceRun) {
 if ($SourceRun -eq $RunId) { throw 'A restart must use a new run directory.' }
 $previous=Join-Path $PSScriptRoot "../../work/runs/$SourceRun"
 if (!(Test-Path (Join-Path $previous cleanup.json))) { throw 'Source run is not cleaned up.' }
 $audit=Get-Content -Raw (Join-Path $previous cold-integrity.json) | ConvertFrom-Json
 if (!$audit.passed -or !$audit.persistence.passed) { throw 'Source disk did not pass the persistence audit.' }
 $disk=Join-Path $previous hdd.qcow2
 $expected=$audit.source_sha256
}
$iso=Join-Path $PSScriptRoot ../native-windows-bootvid-framebuffer/artifacts/bootvid-ram-001.iso
if ((Get-FileHash $disk).Hash -ne $expected) { throw 'Persistence source disk changed.' }
if ((Get-FileHash $iso).Hash -ne '605DD66EFF552538B2940159DDF1E41EC4EFCE9766739E5BD8CA6A0AC833A8EF') { throw 'ISO changed.' }
$capture=@{}
if ($Wide) {
 $eeprom=Join-Path $PSScriptRoot ../../work/paging-v3-widescreen-eeprom.bin
 if ((Get-FileHash $eeprom).Hash -ne '8B4A8A97E21797E2F94EA8C953B1D3432AC91D1D5CC8783C031E3823BAFA924A') { throw 'Wide EEPROM changed.' }
 $capture=@{EepromSource=$eeprom;CaptureWidth=1024;CaptureHeight=576;CapturePitch=4096}
}
& (Join-Path $PSScriptRoot ../native-windows-nt5-kernel/Invoke-Diagnostic.ps1) -RunId $RunId `
 -Bios C:/Emulators/xemu/system/bios/Complex_4627.bin -Iso $iso -HddSource $disk @capture `
 -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -ExerciseInput -UsbMouse -LaunchXromwell -Autorun -RetainDisk -AllowFramebufferFallback -StopOnBugcheck -StopOnCaptureComplete -Seconds 900
if ($LASTEXITCODE) { throw 'Inspect owned emulator run logs.' }
