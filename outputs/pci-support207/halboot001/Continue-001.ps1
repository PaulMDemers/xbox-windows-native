#requires -Version 7.4
$ErrorActionPreference='Stop'
$journal=Join-Path $PSScriptRoot 'pipeline001.json'
if(Test-Path -LiteralPath $journal){throw 'Fresh pipeline required'}
$script:rows=@()
function Stage([string]$Name,[scriptblock]$Action){
 for($attempt=0;$attempt -lt 45;$attempt++){
  try {
   & $Action
   $script:rows+=@{stage=$Name;utc=[DateTime]::UtcNow.ToString('o');result='completed'}
   $script:rows|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $journal
   return
  } catch {
   $message=$_.Exception.Message
   $busy=$message -like "Xbox resource '*' is busy or unavailable*"
   $script:rows+=@{stage=$Name;utc=[DateTime]::UtcNow.ToString('o');result=if($busy){'lease_busy_no_action'}else{'failed'};error=$message}
   $script:rows|ConvertTo-Json -Depth 5|Set-Content -LiteralPath $journal
   if(!$busy){throw}
  }
  Start-Sleep -Seconds 20
 }
 throw "Bounded lease wait expired: $Name"
}
function Linux-Step([string]$Name,[string]$Variant){
 if((Get-PSDrive C).Free - 128MB -lt 20GB){throw 'Projected C reserve below20GiB'}
 & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource build -Action {
  & wsl -d Ubuntu -- env XWN_BUILD_LEASE=held LD_LIBRARY_PATH=/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu python3 ('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/device-workstreams207/pci/repo/outputs/pci-support207/halboot001/'+$Name) $Variant
  if($LASTEXITCODE){throw "$Name failed; preserve attempt"}
 }
}
Stage 'build' { & (Join-Path $PSScriptRoot 'Build-001.ps1') }
Stage 'review' { & C:/Python314/python.exe (Join-Path $PSScriptRoot 'review-build.py');if($LASTEXITCODE){throw 'Review failed'} }
foreach($variant in @('control','candidate')){
 Stage ($variant+'-prepare') { Linux-Step 'prepare-emulator.py' $variant }
 Stage ($variant+'-run') {
  if((Get-PSDrive C).Free - 128MB -lt 20GB){throw 'Projected C reserve below20GiB'}
  & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {
   & C:/Python314/python.exe (Join-Path $PSScriptRoot 'run-emulator.py') $variant
   if($LASTEXITCODE){throw 'Guest run failed; preserve attempt'}
  }
 }
 Stage ($variant+'-audit') { Linux-Step 'audit-emulator.py' $variant }
 Stage ($variant+'-pnp-review') { Linux-Step 'review-pnp.py' $variant }
 $r=Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot ($variant+'001/pnp-review.json'))|ConvertFrom-Json
 if(!$r.qualified_resource_only_installation -or !$r.hal_probe_passed -or !$r.lifecycle_completed){throw "$variant runtime gate failed; no next launch"}
}
