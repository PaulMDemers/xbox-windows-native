#requires -Version 7.4
# Preserve completed, standalone old run disks on the roomy local drive.
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runs=Join-Path $ws 'work/runs'
$archive='E:\Codex-private-artifacts\xbox-windows-feasibility\runs'
$report=Join-Path $PSScriptRoot 'manifest-20261008b.json'
if(Test-Path -LiteralPath $report){throw 'Offload record already exists'}
$names=@('nt5-extended-f-008','nt5-fatx-boot-001')
$records=@()
$activeParents=(Get-Content (Join-Path $ws 'outputs/video-line-gdi/fixture-candidate001.json') -Raw | ConvertFrom-Json).parents.path
foreach($name in $names){if(@($activeParents | Where-Object {$_.Contains($name)}).Count){throw 'Active backing chain would be moved'}}
foreach($name in $names){
    $source=[IO.Path]::GetFullPath((Join-Path $runs $name))
    $backup=[IO.Path]::GetFullPath((Join-Path $runs ($name+'.verified-offload-original')))
    $target=[IO.Path]::GetFullPath((Join-Path $archive $name))
    if(!$source.StartsWith($runs+[IO.Path]::DirectorySeparatorChar) -or !$backup.StartsWith($runs+[IO.Path]::DirectorySeparatorChar) -or !$target.StartsWith($archive+'\')){throw 'Target containment failed'}
    if(!(Test-Path -LiteralPath (Join-Path $source 'cleanup.json'))){throw 'Run not closed'}
    $disk=Join-Path $source 'hdd.qcow2'
    $stream=[IO.File]::OpenRead($disk)
    try {$header=[byte[]]::new(24);if($stream.Read($header,0,24) -ne 24){throw 'Short QCOW header'}} finally {$stream.Dispose()}
    if([Convert]::ToHexString($header[0..3]) -ne '514649FB' -or @($header[8..19] | Where-Object {$_ -ne 0}).Count){throw 'Expected standalone QCOW, no backing path'}
    if(@(Get-CimInstance Win32_Process | Where-Object {$_.Name -like "*xemu*" -and $_.CommandLine -and $_.CommandLine.Contains($name)}).Count){throw 'Owned guest is running'}
    if((Test-Path -LiteralPath $target) -or (Test-Path -LiteralPath $backup)){throw 'Destination already exists'}
    if((Get-Item -LiteralPath $source).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Already redirected'}
    $items=@(Get-ChildItem -LiteralPath $source -Recurse -Force)
    if(@($items | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}).Count){throw 'Nested reparse point'}
    $files=@($items | Where-Object {!$_.PSIsContainer} | ForEach-Object { @{path=[IO.Path]::GetRelativePath($source,$_.FullName); bytes=$_.Length; sha256=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()} })
    $records+=@{name=$name;source=$source;backup=$backup;target=$target;files=$files;status='prepared'}
}
function Save-Report { @{scope='Local verified offload of two completed standalone emulator runs; original paths retained as directory junctions';utc=[DateTime]::UtcNow.ToString('o');records=$records} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $report }
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
