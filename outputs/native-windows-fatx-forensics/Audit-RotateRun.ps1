#requires -Version 7.4
param([Parameter(Mandatory)][ValidatePattern('^nt5-physical-f-high-allocation-[a-z0-9-]+$')][string]$RunId,
      [Parameter(Mandatory)][ValidateRange(1,9)][int]$Boots,
      [string]$FilesystemDriver = "xwnfatx-unlinked.sys")
$ErrorActionPreference='Stop'
$wslRoot='/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility'
& wsl -d Ubuntu -- python3 "$wslRoot/outputs/native-windows-fatx-forensics/audit-rotate.py" --run $RunId --boots $Boots
if ($LASTEXITCODE) { throw 'Rotation audit failed' }
& wsl -d Ubuntu -- python3 "$wslRoot/outputs/native-windows-physical-f/audit-cache-probe.py" --run $RunId *> (Join-Path $PSScriptRoot "build-logs/$RunId-cache-audit.log")
if ($LASTEXITCODE) { throw 'Cache audit failed' }
& wsl -d Ubuntu -- python3 "$wslRoot/outputs/native-windows-extended-storage/audit-cold.py" --run $RunId --probe-version cache --high-allocation-baseline --video-miniport "$wslRoot/outputs/native-windows-physical-f/artifacts/xboxvnt5-trace.sys" --filesystem-driver "$wslRoot/outputs/native-windows-fatx-forensics/artifacts/$FilesystemDriver" *> (Join-Path $PSScriptRoot "build-logs/$RunId-cold-audit.log")
if ($LASTEXITCODE) { throw 'Cold filesystem audit failed' }
$events=Join-Path $PSScriptRoot "$RunId-events.json"
& C:/Python314/python.exe (Join-Path $PSScriptRoot ../native-windows-physical-f/decode-legacy-events.py) (Join-Path $PSScriptRoot "../native-windows-physical-f/artifacts/$RunId-sysevent.evt") --output $events *> (Join-Path $PSScriptRoot "build-logs/$RunId-events.log")
if ($LASTEXITCODE) { throw 'Event decoding failed' }
# Visual observation is supplied separately, after reviewing captured screens.
Write-Output "Cold checks complete. Review screen evidence and qualify with $events."
