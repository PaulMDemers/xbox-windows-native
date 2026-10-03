#requires -Version 7.4
[CmdletBinding()]
param([ValidateSet('toolchain','diagnostic','loader','io','hal-audit','hal-free-audit','cromwell')][string]$Stage = 'diagnostic')
$ErrorActionPreference = 'Stop'
$resource = 'C:\Users\Paul\Desktop\ogxbox-linux\scripts\with_xbox_resource.ps1'
$linuxKit = '/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-prebuild'
& $resource -Resource build -Action {
    if ($Stage -eq 'toolchain') {
        & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash "$linuxKit/bootstrap-toolchain.sh"
    } elseif ($Stage -eq 'cromwell') {
        & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash "$linuxKit/build-cromwell.sh"
    } else {
        & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash "$linuxKit/build-loader.sh" $Stage
    }
    if ($LASTEXITCODE -ne 0) { throw "Build stage $Stage failed with exit code $LASTEXITCODE" }
}
