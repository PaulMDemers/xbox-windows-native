#requires -Version 7.4
$ErrorActionPreference='Stop'
$dest=Join-Path $PSScriptRoot powershell-review001.json
if(Test-Path -LiteralPath $dest){throw 'Review exists'}
$rows=@()
foreach($dir in @((Join-Path $PSScriptRoot '../gpu-reference-pair242'),$PSScriptRoot)){
 foreach($file in (Get-ChildItem -LiteralPath $dir -Filter '*.ps1' -File)){
  $tokens=$null;$errors=$null
  [Management.Automation.Language.Parser]::ParseFile($file.FullName,[ref]$tokens,[ref]$errors) | Out-Null
  if($errors.Count){throw ($errors | Out-String)}
  $rows+=@{file=$file.FullName;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash.ToLowerInvariant();parse_passed=$true}
 }
}
@{passed=$true;files=$rows;physical_access=$false} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $dest -Encoding utf8
Write-Output '242/243 PowerShell source parse PASS'
