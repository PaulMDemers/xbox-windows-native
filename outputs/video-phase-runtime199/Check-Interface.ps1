#requires -Version 7.4
$ErrorActionPreference='Stop'
$path=Join-Path $PSScriptRoot 'Run.ps1'
$dest=Join-Path $PSScriptRoot 'run-interface-review.json'
if(Test-Path $dest){throw 'Already reviewed'}
$taskTokens=$null;$taskErrors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($path,[ref]$taskTokens,[ref]$taskErrors)
if($taskErrors.Count){throw 'Run parser errors'}
$parameter=$ast.ParamBlock.Parameters | Where-Object {$_.Name.VariablePath.UserPath -eq 'Case'}
$attr=$parameter.Attributes | Where-Object {$_.TypeName.Name -eq 'ValidateSet'}
$allowed=@($attr.PositionalArguments | ForEach-Object {$_.Value})
if(($allowed -join ',') -ne 'control001,candidate001'){throw 'Case interface mismatch'}
$text=[IO.File]::ReadAllText($path)
if($text.Contains('-GdbPort') -or !$text.Contains('-Seconds 300') -or !$text.Contains('nt5-phase199-') -or !$text.Contains('video-phase-runtime199-')){throw 'Owned runner contract mismatch'}
[ordered]@{passed=$true;order=@('control001','candidate001');actual_validate_set=$allowed;source_sha256=(Get-FileHash $path).Hash.ToLowerInvariant();parser_errors=0;debugger=$false;physical_access=$false} | ConvertTo-Json | Set-Content $dest
'Actual199 PowerShell case/run/bound contract reviewed'
