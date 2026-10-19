$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$recordPath = Join-Path $PSScriptRoot 'archive-compression001.json'
if (Test-Path -LiteralPath $recordPath) { throw 'Record already exists' }
$active = @(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' -or $_.Name -like 'qemu-system*' })
if ($active.Count) { throw 'An emulator is running' }
$record = [ordered]@{ completed = $false; startedUtc = [DateTime]::UtcNow.ToString('o'); scope = 'NTFS host-file compression only; no guest mount, rerun, recollection, rebasing or new parent'; beforeFreeBytes = (Get-PSDrive C).Free; files = @() }
function Save-Record { $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $recordPath -Encoding utf8 }
Save-Record
foreach ($number in @(561,562,563,564,566)) {
    $root = [IO.Path]::GetFullPath("C:\xwn$number\pc001")
    $disk = (Resolve-Path -LiteralPath (Join-Path $root 'disk.qcow2')).Path
    if ($disk -ne (Join-Path $root 'disk.qcow2')) { throw 'Unexpected resolved disk path' }
    $run = Get-Content -LiteralPath (Join-Path $repo "outputs/rct$number/ntfs-phase1.json") -Raw | ConvertFrom-Json
    $final = Get-Content -LiteralPath (Join-Path $repo "outputs/rct$number/final001.json") -Raw | ConvertFrom-Json
    if (-not $run.closed -or -not $final.closed) { throw 'Runtime not closed' }
    $before = (Get-FileHash -LiteralPath $disk -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($before -ne $run.disk_sha256) { throw 'Archive hash differs before compression' }
    $row = [ordered]@{ path = $disk; bytes = (Get-Item -LiteralPath $disk).Length; beforeSha256 = $before; completed = $false }
    $record.files += $row
    Save-Record
    $output = & compact.exe /C $disk 2>&1
    $row['compactOutput'] = ($output -join "`n")
    $row['exitCode'] = $LASTEXITCODE
    Save-Record
    if ($LASTEXITCODE -ne 0) { throw 'Compression failed; preserve record' }
    $row['afterSha256'] = (Get-FileHash -LiteralPath $disk -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($row.afterSha256 -ne $before) { throw 'Archive bytes changed' }
    $row.completed = $true
    Save-Record
}
$record['afterFreeBytes'] = (Get-PSDrive C).Free
$record['endedUtc'] = [DateTime]::UtcNow.ToString('o')
$record.completed = $true
Save-Record
$record | Select-Object completed,beforeFreeBytes,afterFreeBytes
