#requires -Version 7.4
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
    if ((Get-PSDrive C).Free - 128MB -lt 20GB) { throw 'Projected 20 GiB C guard' }
    $env:XWN_BUILD_LEASE='held'
    $oldWsl=$env:WSLENV
    try {
        $env:WSLENV='XWN_BUILD_LEASE/u'
        & wsl -d Ubuntu -- bash /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207/prepare-source.sh
        if ($LASTEXITCODE) { throw 'Source reconstruction failed' }
    } finally { $env:WSLENV=$oldWsl; Remove-Item Env:XWN_BUILD_LEASE }
}
