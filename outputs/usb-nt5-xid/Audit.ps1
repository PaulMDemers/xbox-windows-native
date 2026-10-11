param([Parameter(Mandatory)][ValidatePattern('^emu[0-9]{3}$')][string]$Case,[ValidateRange(0,600)][int]$WaitSeconds=180)
$ErrorActionPreference='Stop'
$repo=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
if(-not (Test-Path "$repo/work/runs/nt5xid-$Case/cleanup.json")){throw 'Guest still owned or not closed'}
$linux=('/mnt/e'+$PSScriptRoot.Substring(2)).Replace('\','/')
$deadline=[DateTime]::UtcNow.AddSeconds($WaitSeconds);$refusals=@()
while($true) {
 try {
  & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
   if((Get-PSDrive C).Free -lt (20GB+64MB)){throw '20 GiB projected guard'}
   if(-not (Test-Path "$PSScriptRoot/$Case-review.json")) {
    & wsl -d Ubuntu -- python3 -B "$linux/emulator-disk.py" audit $Case
    if($LASTEXITCODE){throw 'Cold extraction/allocation audit failed'}
   }
   if(-not (Test-Path "$PSScriptRoot/$Case/details.json")) {
    & wsl -d Ubuntu -- env LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 -B "$linux/audit-details.py" $Case
    if($LASTEXITCODE){throw 'Cold details audit failed'}
   }
  }
  @{case=$Case;completed=$true;refusals=$refusals;closed_utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Depth 5 | Set-Content "$PSScriptRoot/$Case-audit-lease.json"
  break
 } catch {
  $refusals+=@{utc=[DateTime]::UtcNow.ToString('o');error=$_.ToString()}
  @{case=$Case;completed=$false;refusals=$refusals} | ConvertTo-Json -Depth 5 | Set-Content "$PSScriptRoot/$Case-audit-lease.json"
  if($_.ToString() -notmatch "Xbox resource 'build' is busy" -or [DateTime]::UtcNow -ge $deadline){throw}
  Start-Sleep -Seconds 5
 }
}
