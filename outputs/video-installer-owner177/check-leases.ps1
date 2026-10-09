#requires -Version 7.4
param([Parameter(Mandatory)][ValidateSet('candidate001')][string]$Case,
 [Parameter(Mandatory)][ValidateSet('before','after')][string]$Phase)
$ErrorActionPreference='Stop'
$dest=Join-Path $PSScriptRoot ($Case+'/lease-'+$Phase+'.json')
if(Test-Path $dest){throw 'Already checked'}
$ws=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$instance=Get-Content (Join-Path $ws ('work/runs/nt5-vowner177-'+$Case+'/instance.json')) -Raw | ConvertFrom-Json
if($instance.mode -ne 'exclusive'){throw 'Expected exclusive instance'}
[void](Get-Process -Id $instance.processId -ErrorAction Stop)
$r=[ordered]@{checked_utc=[DateTime]::UtcNow.ToString('o');instance_pid=$instance.processId;instance_mode=$instance.mode;build_conflict=$false;xemu_conflict=$false}
foreach($resource in @('build','xemu')){
 $lock=Join-Path $env:LOCALAPPDATA ('ogxbox-linux/locks/'+$resource+'.lock')
 if(!(Test-Path $lock)){throw 'Resource lock absent'}
 $handle=$null
 try{$handle=[IO.File]::Open($lock,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)}
 catch [IO.IOException]{$r[$resource+'_conflict']=$true}
 finally{if($handle){$handle.Dispose()}}
}
$r | ConvertTo-Json | Set-Content $dest
if(!$r.build_conflict -or !$r.xemu_conflict){throw 'Actual isolation locks did not hold'}
'Actual build and exclusive xemu locks held'
