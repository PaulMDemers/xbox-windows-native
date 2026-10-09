#requires -Version 7.4
# Static host contract checks; never acquire leases or launch a guest.
$ErrorActionPreference='Stop'
$rows=@()
foreach($name in @('Run.ps1','check-leases.ps1')){
 $p=Join-Path $PSScriptRoot $name
 $tokens=$null;$errors=$null
 $ast=[Management.Automation.Language.Parser]::ParseFile($p,[ref]$tokens,[ref]$errors)
 if($errors.Count){throw 'PowerShell syntax errors'}
 $parameter=$ast.ParamBlock.Parameters | Where-Object {$_.Name.VariablePath.UserPath -eq 'Case'}
 if(@($parameter).Count -ne 1){throw 'Exact Case parameter required'}
 $attribute=$parameter.Attributes | Where-Object {$_.TypeName.FullName -eq 'ValidateSet'}
 $values=@($attribute.PositionalArguments | ForEach-Object {$_.Value})
 if(($values -join ',') -ne 'control001,candidate001'){throw 'Both cases must be admitted before bootstrap'}
 $rows+=@{file=$name;sha256=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant();case_values=$values}
}
$dest=Join-Path $PSScriptRoot host-contract.json
if(Test-Path $dest){throw 'Contract already reviewed'}
@{passed=$true;physical_access=$false;guest_launched=$false;checks=$rows} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $dest
'Both actual PowerShell AST case validators reviewed'
