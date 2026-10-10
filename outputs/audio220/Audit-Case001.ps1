#requires -Version 7.4
param([ValidateSet('install001','playback001','restored001')][string]$Case)
$ErrorActionPreference='Stop'
$entered=$false
for($attempt=1;$attempt -le 30;$attempt++) {
    try {
        & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
            $script:entered=$true
            if((Get-PSDrive C).Free-128MB -lt 20GB){throw 'Projected C reserve guard'}
            & python -c "import sys;sys.path.insert(0,'outputs/audio220');from common001 import pins;pins()"
            if($LASTEXITCODE){throw 'Physical frozen input verification failed'}
            & python outputs/native-windows-fatx-preflight/analyze.py --capture "outputs/audio220/artifacts/$Case/allocation" --output "outputs/audio220/$Case/allocation.json"
            if($LASTEXITCODE){throw 'Allocation analysis failed; preserve attempt'}
            if($Case -ne 'restored001') {
                & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 /mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/audio/repo/outputs/audio220/audit001.py $Case
                if($LASTEXITCODE){throw 'Physical cold audit failed; preserve attempt'}
            }
        }
        exit 0
    } catch {
        if($entered -or $_.Exception.Message -notlike "Xbox resource 'build' is busy or unavailable*"){throw}
        Write-Output ('Physical case audit lease contention '+$attempt+' '+[DateTime]::UtcNow.ToString('o'))
        Start-Sleep -Seconds 30
    }
}
throw 'Physical case audit lease wait exhausted'
