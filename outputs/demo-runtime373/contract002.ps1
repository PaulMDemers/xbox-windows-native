#requires -Version 7.4
$ErrorActionPreference='Stop'
$result=Join-Path $PSScriptRoot host-contract002.json
if(Test-Path $result){throw 'Consumed contract ID'}
$files=@('Run.ps1','Invoke.ps1');$counts=@{}
foreach($name in $files){
 $tokens=$null;$errors=$null
 $ast=[Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot $name),[ref]$tokens,[ref]$errors)
 if($errors.Count){throw ($errors | Out-String)}
 $counts[$name]=$ast.FindAll({param($n) $n -is [Management.Automation.Language.CommandAst]},$true).Count
}
$run=Get-Content (Join-Path $PSScriptRoot Run.ps1) -Raw
$invoke=Get-Content (Join-Path $PSScriptRoot Invoke.ps1) -Raw
$close=Get-Content (Join-Path $PSScriptRoot close-host.py) -Raw
$super=Get-Content (Join-Path $PSScriptRoot supervise.py) -Raw
if($run -notmatch 'control001' -or $run -notmatch 'candidate001' -or $run -notmatch 'Case' -or $run -notmatch '5258'){throw 'Case/port contract'}
if($invoke -notmatch 'C:/xwn373/runs' -or $invoke -notmatch 'C:/xwn373/instances' -or $invoke -notmatch 'C:/xwn373/scratch'){throw 'Owned root contract'}
if($close -notmatch 'port==5256' -or $super -notmatch 'C:/xwn373/runs/nt5-demo373-' -or $super -notmatch "127.0.0.1.*5258"){throw 'Host path/port mismatch'}
if($run -match '-Autorun|-LaunchXromwell' -or ([regex]::Matches($super,[regex]::Escape('f.sendcmd(row'))).Count -ne 1){throw 'Duplicate launch path'}
@{passed=$true;actual_ps_ast_counts=$counts;owned_root='C:/xwn373';monitor=5256;gdb=5257;ftp=5258;only_loopback_launch=$true;case_modes=@{control001=1;candidate001=1};runtime=$false} | ConvertTo-Json -Depth 5 | Set-Content $result
