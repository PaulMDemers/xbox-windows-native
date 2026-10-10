#requires -Version 7.4
# Preserve completed, standalone old run disks on the roomy local drive.
# Single CLOSED historical run; no new guest or qualification.
$ErrorActionPreference='Stop'
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$runs=Join-Path $ws 'work/runs'
$archive='E:\Codex-private-artifacts\xbox-windows-feasibility\runs'
$report=Join-Path $PSScriptRoot 'manifest-kernel032035-20261010.json'
if(Test-Path -LiteralPath $report){throw 'Offload record already exists'}
$names=@('nt5-kernel-032','nt5-kernel-035')
$pinmap=@{
 'nt5-kernel-032'=@{cleanup='cb130ab61ea518f0e59f9d78160f2569d4f14fe155a79cf4a4da55e918950696';instance='5cf6f4ad65b685c19b0024a49d90639effbf4cb401c9bbeaa1ea64badfaca1d9'}
 'nt5-kernel-035'=@{cleanup='00bdf53e1014e78463861d3acd8d62f94061df60bd6f60a612a002ce6a67f562';instance='276b37af18e02b52b8a9be426095e0e2a5cd15127fad1f76c983179e7fc18fa6'}
}
$records=@()
# Exact historical cleanup/instance pins, closed standalone disk only.
foreach($name in $names){
    $source=[IO.Path]::GetFullPath((Join-Path $runs $name))
    $backup=[IO.Path]::GetFullPath((Join-Path $runs ($name+'.verified-offload-original')))
    $target=[IO.Path]::GetFullPath((Join-Path $archive $name))
    if(!$source.StartsWith($runs+[IO.Path]::DirectorySeparatorChar) -or !$backup.StartsWith($runs+[IO.Path]::DirectorySeparatorChar) -or !$target.StartsWith($archive+'\')){throw 'Target containment failed'}
    if(!(Test-Path -LiteralPath (Join-Path $source 'cleanup.json'))){throw 'Run not closed'}
    $closedMeta=Get-Content (Join-Path $source 'cleanup.json') -Raw | ConvertFrom-Json
    if(!$closedMeta.completedUtc){throw 'Expected completed owned run'}
    $newParent=Get-Content (Join-Path $ws 'outputs/video-gpu-handoff216/fixture-control001.json') -Raw | ConvertFrom-Json
    foreach($parent in @($newParent.parent)){if($parent.Contains($name)){throw 'Active new fixture references old run'}}
    if((Get-FileHash (Join-Path $source 'cleanup.json')).Hash.ToLowerInvariant() -ne $pinmap[$name].cleanup){throw 'Closed cleanup pin changed'}
    if((Get-FileHash (Join-Path $source 'instance.json')).Hash.ToLowerInvariant() -ne $pinmap[$name].instance){throw 'Historical instance pin changed'}
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
function Save-Report { @{scope='Local verified offload of two CLOSED historical standalone kernel032/035 runs; preserve original evidence without new cold or Windows qualification; no backing-chain relocation; original paths retained as directory junctions';utc=[DateTime]::UtcNow.ToString('o');records=$records} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $report }
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
