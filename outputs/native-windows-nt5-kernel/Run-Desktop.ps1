#requires -Version 7.4
[CmdletBinding()]
param(
    [ValidatePattern('^[a-z0-9-]+$')][string]$RunId = ('desktop-' + (Get-Date -Format 'yyyyMMdd-HHmmss')),
    [ValidateRange(120,3600)][int]$Seconds = 600
)
$ErrorActionPreference='Stop'
$iso=Join-Path $PSScriptRoot 'artifacts/kernel-autorun-006.iso'
$disk=Join-Path $PSScriptRoot 'artifacts/windows2000-integrated-001.qcow2'
$expected=@{
    $iso='2D6F0D0813DCB12A29ECB8D8693CDD4F424B26D0D7B9BDE746AF88DE14A67180'
    $disk='640DA2CCFE86774DD512D846D9674F19D7E642C0DF008CA42952E97185E4445B'
}
foreach ($path in $expected.Keys) {
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash -ne $expected[$path]) {
        throw "The validated input changed: $path"
    }
}
Write-Host "Starting the native Windows Xbox emulator test for $Seconds seconds. Guest disk changes are discarded afterward."
& (Join-Path $PSScriptRoot 'Invoke-Diagnostic.ps1') -RunId $RunId `
    -Bios 'C:/Emulators/xemu/system/bios/Complex_4627.bin' -Iso $iso -HddSource $disk `
    -FtpPort 4596 -MonitorPort 4594 -GdbPort 4595 -LaunchXromwell -UsbMouse `
    -Autorun -TracePackets -CaptureAudio -ExerciseInput -Seconds $Seconds
if ($LASTEXITCODE -ne 0) { throw 'Desktop test failed; inspect its private run logs.' }
