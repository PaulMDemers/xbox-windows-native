#requires -Version 7.4
$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 if((Get-PSDrive C).Free-128MB -lt 20GB){throw 'Projected C reserve guard'}
 & wsl -d Ubuntu -- bash -lc 'cd /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility && python3 -B outputs/demo-audio-level256/build003.py'
 if($LASTEXITCODE){throw 'Diagnostic build/waveform verification failed'}
}
