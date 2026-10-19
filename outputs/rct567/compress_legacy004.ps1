$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$recordPath = Join-Path $PSScriptRoot 'archive-compression004.json'
if (Test-Path -LiteralPath $recordPath) { throw 'Record already exists' }
if (@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' -or $_.Name -like 'qemu-system*' }).Count) { throw 'Emulator running' }
$record = [ordered]@{ completed=$false; startedUtc=[DateTime]::UtcNow.ToString('o'); scope='Host compression of legacy pinned input containers; exact paths and bytes retained; no guest mount or runtime reuse'; beforeFreeBytes=(Get-PSDrive C).Free; files=@() }
function Save-Record { $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $recordPath -Encoding utf8 }
Save-Record
foreach ($stem in @('physical-processinit','physical-mmcomplete','physical-bootvideo')) {
    $wanted = [IO.Path]::GetFullPath((Join-Path $repo "work/$stem-good.qcow2"))
    $disk = (Resolve-Path -LiteralPath $wanted).Path
    if ($disk -ne $wanted -or -not $disk.StartsWith((Join-Path $repo 'work\'))) { throw 'Unexpected path' }
    $manifest = Join-Path $repo "work/runs/$stem-normal-001/input-hashes.json"
    $pins = @(Get-Content -LiteralPath $manifest -Raw | ConvertFrom-Json -AsHashtable)
    $pin = @($pins | Where-Object { $_.Path -eq $disk })
    if ($pin.Count -ne 1) { throw 'Expected one source pin' }
    $before = (Get-FileHash -LiteralPath $disk -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($before -ne $pin[0].Hash.ToLowerInvariant()) { throw 'Pin mismatch' }
    $row = [ordered]@{ path=$disk; manifest=$manifest; bytes=(Get-Item -LiteralPath $disk).Length; beforeSha256=$before; completed=$false }
    $record.files += $row
    Save-Record
    $output = & compact.exe /C $disk 2>&1
    $row['exitCode']=$LASTEXITCODE
    $row['compactOutput']=($output -join "`n")
    Save-Record
    if ($row.exitCode -ne 0) { throw 'Compression failed' }
    $row['afterSha256']=(Get-FileHash -LiteralPath $disk -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($row.afterSha256 -ne $before) { throw 'Bytes changed' }
    $row.completed=$true
    Save-Record
}
$record['afterFreeBytes']=(Get-PSDrive C).Free
$record['endedUtc']=[DateTime]::UtcNow.ToString('o')
$record.completed=$true
Save-Record
Write-Output ('Free bytes: '+$record.afterFreeBytes)
