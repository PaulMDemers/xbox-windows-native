$ErrorActionPreference = 'Stop'
$kit = $PSScriptRoot
$repo = [IO.Path]::GetFullPath((Join-Path $kit '../..'))
$work = [IO.Path]::GetFullPath((Join-Path $repo 'work'))
$inventory = Get-Content -LiteralPath (Join-Path $kit 'inventory001.json') -Raw | ConvertFrom-Json
$receipt = Join-Path $kit 'cleanup001.json'
if (Test-Path -LiteralPath $receipt) { throw 'Cleanup identity already used' }
if ($inventory.dependent_active_disks.Count -ne 0 -or $inventory.selected.Count -ne 6) { throw 'Invalid selection' }
$live = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(xemu|qemu)' }
if ($live) { throw 'Emulator process active' }
$expected = @('physical-bootvideo-bad-hal.qcow2','physical-bootvideo-bad-kernel.qcow2','physical-mmcomplete-bad-hal.qcow2','physical-mmcomplete-bad-kernel.qcow2','physical-processinit-bad-hal.qcow2','physical-processinit-bad-kernel.qcow2')
# Validate every exact target and hash before any deletion. No recursive deletion.
foreach ($row in $inventory.selected) {
    $target = [IO.Path]::GetFullPath($row.path)
    if ([IO.Path]::GetDirectoryName($target) -ne $work -or [IO.Path]::GetFileName($target) -notin $expected) { throw 'Target outside exact allowlist' }
    $item = Get-Item -LiteralPath $target -Force
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $item.Length -ne $row.metadata.bytes) { throw 'Target identity changed' }
    $parent = $item.Directory
    while ($null -ne $parent) {
        if ($parent.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse parent' }
        $parent = $parent.Parent
    }
    if ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $row.metadata.sha256) { throw 'Target hash changed' }
}
$result = [ordered]@{ started_utc=[DateTime]::UtcNow.ToString('o'); free_c_before=([IO.DriveInfo]::new('C')).AvailableFreeSpace; deleted=@(); completed=$false }
$result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receipt -Encoding utf8
foreach ($row in $inventory.selected) {
    Remove-Item -LiteralPath $row.path -Force
    if (Test-Path -LiteralPath $row.path) { throw 'Removal did not complete' }
    $result.deleted += [ordered]@{ path=$row.path; sha256=$row.metadata.sha256; bytes=$row.metadata.bytes; allocated_bytes=$row.metadata.allocated_bytes }
    $result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receipt -Encoding utf8
}
$result.free_c_after=([IO.DriveInfo]::new('C')).AvailableFreeSpace
$result.free_c_delta=$result.free_c_after-$result.free_c_before
$result.completed=$true
$result.finished_utc=[DateTime]::UtcNow.ToString('o')
$result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $receipt -Encoding utf8
$result | ConvertTo-Json -Depth 10
