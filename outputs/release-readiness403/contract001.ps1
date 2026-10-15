#requires -Version 7.4
$ErrorActionPreference='Stop'
$result=Join-Path $PSScriptRoot host-contract001.json
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
if($run -notmatch 'emu001' -or $run -notmatch 'Case' -or $run -notmatch '5408'){throw 'Case/port contract'}
if($invoke -notmatch 'C:/xwn403/runs' -or $invoke -notmatch 'C:/xwn403/instances' -or $invoke -notmatch 'C:/xwn403/scratch'){throw 'Owned root contract'}
if($close -notmatch 'port==5406' -or $super -notmatch 'C:/xwn403/runs/nt5-restore403-' -or $super -notmatch "127.0.0.1.*5408"){throw 'Host path/port mismatch'}
if($run -match '-Autorun|-LaunchXromwell' -or ([regex]::Matches($super,[regex]::Escape('f.sendcmd(row'))).Count -ne 1){throw 'Duplicate launch path'}
@{passed=$true;actual_ps_ast_counts=$counts;owned_root='C:/xwn403';monitor=5406;gdb=5407;ftp=5408;only_loopback_launch=$true;case_modes=@{emu001=1};runtime=$false} | ConvertTo-Json -Depth 5 | Set-Content $result
