#requires -Version 7.4
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    if ((Get-PSDrive C).Free - 128MB -lt 20GB) { throw 'Projected 20 GiB C guard' }
    & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207/build-driver.sh
    if ($LASTEXITCODE) { throw 'Audio207 build failed; retain log' }
}
