param([ValidateSet('open','close')][string]$Action)
$ErrorActionPreference='Stop'
$kitPath=Split-Path -Parent $MyInvocation.MyCommand.Path
$cfg=Get-Content -LiteralPath C:/xwn657/config.json -Raw | ConvertFrom-Json
$ruleName='XWN657-owned-UDP'
if($Action -eq 'open') {
 $outPath=Join-Path $kitPath firewall-open001.json
 if(Test-Path -LiteralPath $outPath){throw 'Existing attempt'}
 $record=@{passed=$false;utc=[DateTime]::UtcNow.ToString('o');rule=$ruleName;scope='UDP50657 inbound from configured Xbox only, Python314, resolved LAN interface';temporary=$true}
 try {
  if(Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue){throw 'Rule already exists'}
  $iface=(Get-NetIPAddress -AddressFamily IPv4 -IPAddress $cfg.host).InterfaceAlias
  New-NetFirewallRule -Name $ruleName -DisplayName $ruleName -Direction Inbound -Action Allow -Protocol UDP -LocalPort $cfg.port -RemoteAddress $cfg.expected_peer -Program C:\Python314\python.exe -InterfaceAlias $iface -Profile Any | Out-Null
  $rule=Get-NetFirewallRule -Name $ruleName
  if($rule.Enabled -ne 'True' -or $rule.Action -ne 'Allow'){throw 'Readback failed'}
  $record.passed=$true
 } catch {$record.failure=$_.Exception.Message;throw} finally {$record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $outPath -Encoding UTF8}
} else {
 $outPath=Join-Path $kitPath firewall-close001.json
 if(Test-Path -LiteralPath $outPath){throw 'Existing close'}
 Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule
 if(Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue){throw 'Rule still exists'}
 @{removed=$true;rule=$ruleName;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $outPath -Encoding UTF8
}
