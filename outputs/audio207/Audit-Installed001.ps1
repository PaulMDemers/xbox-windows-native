#requires -Version 7.4
param([ValidateSet('installed001')][string]$Case)
$ErrorActionPreference='Stop'
$state=@{entered=$false}
for($attempt=1;$attempt -le 20;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $state.entered=$true
            & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio207/audit-installed001.py $Case
            if($LASTEXITCODE){throw 'Cold audit failed; preserve attempt and do not retry'}
        }
        exit 0
    } catch {
        if($state.entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Audit prelaunch lease contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Audit lease wait exhausted without disk access'
