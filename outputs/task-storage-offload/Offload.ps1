#requires -Version 7.4
# Preserve completed, standalone old run disks on the roomy local drive.
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runs=Join-Path $ws 'work/runs'
$archive='E:\Codex-private-artifacts\xbox-windows-feasibility\runs'
$report=Join-Path $PSScriptRoot 'manifest.json'
if(Test-Path -LiteralPath $report){throw 'Offload record already exists'}
$names=@('nt5-kernel-051','nt5-kernel-052','nt5-kernel-053','nt5-kernel-054')
$records=@()
foreach($name in $names){
    $source=[IO.Path]::GetFullPath((Join-Path $runs $name))
    $backup=[IO.Path]::GetFullPath((Join-Path $runs ($name+'.verified-offload-original')))
    $target=[IO.Path]::GetFullPath((Join-Path $archive $name))
    if(!$source.StartsWith($runs+[IO.Path]::DirectorySeparatorChar) -or !$backup.StartsWith($runs+[IO.Path]::DirectorySeparatorChar) -or !$target.StartsWith($archive+'\')){throw 'Target containment failed'}
    if(!(Test-Path -LiteralPath (Join-Path $source 'cleanup.json'))){throw 'Run not closed'}
    if((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath $backup)){throw 'Destination already exists'}
    if((Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Already redirected'}
    $items=@(Get-ChildItem -LiteralPath $source -Recurse -Force)
    if(@($items | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Nested reparse point'}
    $files=@($items | Where-Object {!$_.PSIsContainer} | ForEach-Object { @{path=[IO.Path]::GetRelativePath($source,$_.FullName); bytes=$_.Length; sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} })
    $records+=@{name=$name;source=$source;backup=$backup;target=$target;files=$files;status='prepared'}
}
function Save-Report { @{scope='Local verified offload of four completed standalone emulator runs; original paths retained as directory junctions';utc=[DateTime]::UtcNow.ToString('o');records=$records} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $report }
Save-Report
New-Item -ItemType Directory -Path $archive -Force | Out-Null
foreach($row in $records){
    Copy-Item -LiteralPath $row.source -Destination $row.target -Recurse
    foreach($file in $row.files){$copy=Join-Path $row.target $file.path;if((Get-FileHash -LiteralPath $copy).Hash.ToLowerInvariant() -ne $file.sha256){throw 'Copied content mismatch'}}
    $row.status='copy_verified';Save-Report
    # Every absolute source/backup/target was checked above before the move.
    Move-Item -LiteralPath $row.source -Destination $row.backup
    try {
        New-Item -ItemType Junction -Path $row.source -Target $row.target | Out-Null
        foreach($file in $row.files){$copy=Join-Path $row.source $file.path;if((Get-FileHash -LiteralPath $copy).Hash.ToLowerInvariant() -ne $file.sha256){throw 'Junction readback mismatch'}}
    } catch { throw "Original remains at $($row.backup); copied files remain at $($row.target). $($_.Exception.Message)" }
    $row.status='junction_verified';Save-Report
    $checked=[IO.Path]::GetFullPath($row.backup)
    if(!$checked.StartsWith($runs+[IO.Path]::DirectorySeparatorChar) -or (Get-Item -LiteralPath $checked).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Delete containment failed'}
    Remove-Item -LiteralPath $checked -Recurse -Force
    $row.status='complete';Save-Report
    Write-Output ($row.name+': copied, hash-verified, original path preserved')
}
