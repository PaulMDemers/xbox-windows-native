#requires -Version 7.4
$ErrorActionPreference='Stop'
$journal=Join-Path $PSScriptRoot 'pipeline001.json'
if(Test-Path -LiteralPath $journal){throw 'Fresh pipeline journal required'}
$script:stageRows=@()
function Invoke-Stage([string]$Name,[scriptblock]$Action){
 for($attempt=0;$attempt -lt 45;$attempt++){
  try {
   & $Action
   $script:stageRows+=@{stage=$Name;utc=[DateTime]::UtcNow.ToString('o');result='completed'}
   $script:stageRows|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $journal
   return
  } catch {
   $message=$_.Exception.Message
   $busy=$message -like "Xbox resource '*' is busy or unavailable*"
   $script:stageRows+=@{stage=$Name;utc=[DateTime]::UtcNow.ToString('o');result=if($busy){'lease_busy_no_action'}else{'failed'};error=$message}
   $script:stageRows|ConvertTo-Json -Depth 4|Set-Content -LiteralPath $journal
   if(!$busy){throw}
  }
  Start-Sleep -Seconds 20
 }
 throw "Bounded lease wait expired at $Name"
}
Invoke-Stage 'build' { & (Join-Path $PSScriptRoot 'Build-001.ps1') }
Invoke-Stage 'static_review' { & C:/Python314/python.exe (Join-Path $PSScriptRoot 'review-build.py');if($LASTEXITCODE){throw 'Static review failed'} }
Invoke-Stage 'prepare' { & (Join-Path $PSScriptRoot 'Prepare-Emulator001.ps1') }
Invoke-Stage 'run' { & (Join-Path $PSScriptRoot 'Run-Emulator001.ps1') }
Invoke-Stage 'audit' { & (Join-Path $PSScriptRoot 'Audit-Pnp001.ps1') }
