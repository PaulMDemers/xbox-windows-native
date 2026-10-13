#requires -Version 7.4
$ErrorActionPreference='Stop'
$workspace=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$allowed=@($workspace, 'E:\Codex-archive\xbox-windows-native','E:\Codex-private-artifacts\xbox-windows-feasibility')
$plan=Get-Content -LiteralPath E:/xwn328/archive-plan002.json -Raw | ConvertFrom-Json
$journal='E:/xwn328/archive-journal002.jsonl'
if(Test-Path -LiteralPath $journal){throw 'Consumed archive attempt'}
& C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
  if(@(Get-Process xemu*,qemu-system* -ErrorAction SilentlyContinue).Count){throw 'Emulator still running'}
  foreach($row in @($plan.logs)+@($plan.disks)) {
   $path=[IO.Path]::GetFullPath($row.path)
   if(-not @($allowed | Where-Object { $path.StartsWith($_+'\',[StringComparison]::OrdinalIgnoreCase) }).Count){throw 'Outside allowed roots'}
   if([IO.Path]::GetExtension($path) -notin @('.log','.qcow2')){throw 'Unexpected extension'}
   $item=Get-Item -LiteralPath $path
   if($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -or $item.Length -ne $row.bytes){throw 'Changed target'}
   $walk=$item.Directory
   while($walk) {if($walk.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=$walk.Parent}
   # Deny writers throughout compression/verification, permitting only reads.
   $hold=[IO.File]::Open($path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
   try {
    $raw=& C:/Python314/python.exe -B (Join-Path $PSScriptRoot archive-file.py) $path
    if($LASTEXITCODE){throw 'Archive failed; retain source and partial output'}
    $proof=$raw | ConvertFrom-Json
    if(-not $proof.roundtrip_verified -or $proof.original_bytes -ne $item.Length -or $proof.source -ne $path){throw 'Archive receipt mismatch'}
   } finally {$hold.Dispose()}
   # File-only removal, in this same shell, after full-path and byte verification.
   $proof | ConvertTo-Json -Compress | Add-Content -LiteralPath $journal
   if($proof.archive_bytes -lt $proof.original_bytes) {
    Remove-Item -LiteralPath $path
    $proof.source_removed=$true
    $proof | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath ($path+'.archived328.json')
   }
   $proof | ConvertTo-Json -Compress | Add-Content -LiteralPath $journal
   Write-Output ('Archived {0}: reclaimed {1:N0} bytes' -f $path,($proof.original_bytes-$proof.archive_bytes))
  }
 }
}
