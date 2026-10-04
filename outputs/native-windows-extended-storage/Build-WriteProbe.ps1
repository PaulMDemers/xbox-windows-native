#requires -Version 7.4
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot artifacts) | Out-Null
& 'C:\Users\Paul\Desktop\ogxbox-linux\scripts\with_xbox_resource.ps1' -Resource build -Action {
 & wsl -d Ubuntu -- /home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc -Os -nostdlib -fno-stack-protector -fno-builtin '-Wl,--entry,_mainCRTStartup@0' '-Wl,--subsystem,console:5.0' -o /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-extended-storage/artifacts/xwnlargewrite.exe /mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/outputs/native-windows-extended-storage/xwnlargewrite.c -lkernel32 -ladvapi32 -luser32
 if ($LASTEXITCODE -ne 0) { throw 'Guest checker build failed' }
}
