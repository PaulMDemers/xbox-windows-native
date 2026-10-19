$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$recordPath = Join-Path $PSScriptRoot 'archive-compression003.json'
if (Test-Path -LiteralPath $recordPath) { throw 'Record already exists' }
if (@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' -or $_.Name -like 'qemu-system*' }).Count) { throw 'Emulator running' }
$record = [ordered]@{ completed=$false; startedUtc=[DateTime]::UtcNow.ToString('o'); scope='Host compression of closed immutable fixture containers only; no mounts, new parents, runtime access or path changes'; beforeFreeBytes=(Get-PSDrive C).Free; files=@() }
function Save-Record { $record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $recordPath -Encoding utf8 }
Save-Record
$entries = @('stretch-runtime371/control001','stretch-runtime371/candidate001','demo-runtime373/control001','demo-runtime377/control001','file-enumeration389/control001','file-enumeration391/candidate001','file-enumeration392/candidate001','cmd-regression393/candidate001')
foreach ($entry in $entries) {
    $dir = Join-Path $repo "outputs/$entry"
    $closure = Get-Content -LiteralPath (Join-Path $dir 'closure.json') -Raw | ConvertFrom-Json -AsHashtable
    $fixture = Get-Content -LiteralPath (Join-Path $dir 'fixture.json') -Raw | ConvertFrom-Json -AsHashtable
    if (-not $closure.closed) { throw 'Fixture runtime not closed' }
    $wanted = [IO.Path]::GetFullPath($fixture.fixture_path_windows)
    if ($wanted -notmatch '^C:\\xwn(371|373|377|389|391|392|393)\\(control001|candidate001)\\source\.qcow2$') { throw 'Unexpected source location' }
    $disk = (Resolve-Path -LiteralPath $wanted).Path
    if ($disk -ne $wanted) { throw 'Unexpected resolved path' }
    $before = (Get-FileHash -LiteralPath $disk -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($before -ne $fixture.fixture_sha256) { throw 'Fixture pin mismatch' }
    $row = [ordered]@{ path=$disk; fixtureRecord="$entry/fixture.json"; bytes=(Get-Item -LiteralPath $disk).Length; beforeSha256=$before; completed=$false }
    $record.files += $row
    Save-Record
    $output = & compact.exe /C $disk 2>&1
    $row['exitCode'] = $LASTEXITCODE
    $row['compactOutput'] = ($output -join "`n")
    Save-Record
    if ($row.exitCode -ne 0) { throw 'Compression failed' }
    $row['afterSha256'] = (Get-FileHash -LiteralPath $disk -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($row.afterSha256 -ne $before) { throw 'Bytes changed' }
    $row.completed = $true
    Save-Record
}
$record['afterFreeBytes'] = (Get-PSDrive C).Free
$record['endedUtc'] = [DateTime]::UtcNow.ToString('o')
$record.completed = $true
Save-Record
Write-Output ('Free bytes: ' + $record.afterFreeBytes)
