#requires -Version 7.4
$ErrorActionPreference='Stop'
& 'C:\Users\Paul\Desktop\ogxbox-linux\scripts\with_xbox_resource.ps1' -Resource build -Action {
    & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held bash /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-nt5-kernel/build-autorun.sh
    if ($LASTEXITCODE -ne 0) { throw 'Kernel diagnostic build failed' }
}
