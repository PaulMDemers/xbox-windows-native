$ErrorActionPreference='Stop'
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held python3 -B /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/fatx-enumeration390/build.py --source-cache /home/paul/xbox-windows-native/sources/reactos-extended --rosbe /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1 --output /home/paul/xbox-windows-native/build/fatx-enumeration390-001 --profile fatx --jobs 4
 if($LASTEXITCODE -ne 0){throw 'Candidate build failed; preserve unique attempt'}
}
