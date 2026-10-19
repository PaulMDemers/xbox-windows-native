$ErrorActionPreference='Stop'
$repo=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
$recordPath=Join-Path $PSScriptRoot 'archive-compression002.json'
if(Test-Path -LiteralPath $recordPath){throw 'Record exists'}
if(@(Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'xemu*' -or $_.Name -like 'qemu-system*' }).Count){throw 'Emulator active'}
$plan=Get-Content (Join-Path $PSScriptRoot 'archive-plan002.json') -Raw | ConvertFrom-Json -AsHashtable
$record=[ordered]@{completed=$false; startedUtc=[DateTime]::UtcNow.ToString('o'); beforeFreeBytes=(Get-PSDrive C).Free; planSha256=(Get-FileHash (Join-Path $PSScriptRoot 'archive-plan002.json')).Hash.ToLowerInvariant(); files=@()}
function Save-Record {$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $recordPath -Encoding utf8}
Save-Record
foreach($item in $plan.files){
 if((Get-PSDrive C).Free -ge 23GB){break}
 $disk=(Resolve-Path -LiteralPath $item.path).Path
 if($disk -ne $item.path -or [IO.Path]::GetDirectoryName($disk) -ne (Join-Path $repo 'work') -or [IO.Path]::GetFileName($disk) -notlike 'physical-*.qcow2'){throw 'Unexpected path'}
 $before=(Get-FileHash -LiteralPath $disk).Hash.ToLowerInvariant()
 if($before -ne $item.sha256){throw 'Source pin mismatch'}
 $row=[ordered]@{path=$disk; beforeSha256=$before; bytes=$item.bytes; completed=$false}
 $record.files+=$row
 Save-Record
 $output=& compact.exe /C $disk 2>&1
 $row['exitCode']=$LASTEXITCODE
 $row['compactOutput']=($output -join "`n")
 Save-Record
 if($row.exitCode -ne 0){throw 'Compression failed'}
 $row['afterSha256']=(Get-FileHash -LiteralPath $disk).Hash.ToLowerInvariant()
 if($row.afterSha256 -ne $before){throw 'Bytes changed'}
 $row.completed=$true
 Save-Record
}
$record['afterFreeBytes']=(Get-PSDrive C).Free
$record['endedUtc']=[DateTime]::UtcNow.ToString('o')
$record.completed=$true
Save-Record
Write-Output ('Free bytes: '+$record.afterFreeBytes)
