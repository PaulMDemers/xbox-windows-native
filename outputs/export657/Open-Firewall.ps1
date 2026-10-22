# Run once from an Administrator PowerShell. No launch or credential access.
$ErrorActionPreference='Stop'
$kitPath=Split-Path -Parent $MyInvocation.MyCommand.Path
$outPath=Join-Path $kitPath firewall-open002.json
if(Test-Path -LiteralPath $outPath){throw 'Attempt already recorded; preserve its outcome.'}
$cfg=Get-Content -LiteralPath C:/xwn657/config.json -Raw | ConvertFrom-Json
$ruleName='XWN657-owned-UDP'
$record=@{passed=$false;utc=[DateTime]::UtcNow.ToString('o');rule=$ruleName;scope='UDP50657 inbound from configured Xbox only, Python314, resolved LAN interface';temporary=$true}
try {
 if(Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue){throw 'Rule already exists'}
 if($cfg.port -ne 50657){throw 'Unexpected port'}
 $iface=(Get-NetIPAddress -AddressFamily IPv4 -IPAddress $cfg.host -ErrorAction Stop).InterfaceAlias
 New-NetFirewallRule -Name $ruleName -DisplayName $ruleName -Direction Inbound -Action Allow -Protocol UDP -LocalPort 50657 -RemoteAddress $cfg.expected_peer -Program C:\Python314\python.exe -InterfaceAlias $iface -Profile Any -ErrorAction Stop | Out-Null
 $rule=Get-NetFirewallRule -Name $ruleName -ErrorAction Stop
 $port=$rule | Get-NetFirewallPortFilter
 $addr=$rule | Get-NetFirewallAddressFilter
 $app=$rule | Get-NetFirewallApplicationFilter
 $intf=$rule | Get-NetFirewallInterfaceFilter
 if($rule.Enabled -ne 'True' -or $rule.Action -ne 'Allow' -or $rule.Direction -ne 'Inbound' -or $port.Protocol -ne 'UDP' -or $port.LocalPort -ne '50657' -or $addr.RemoteAddress -ne $cfg.expected_peer -or $app.Program -ne 'C:\Python314\python.exe' -or $intf.InterfaceAlias -ne $iface){throw 'Exact scoped rule readback failed'}
 $record.passed=$true
 $cleanupScript=Join-Path $kitPath Close-Firewall.ps1
 $cleanup=Start-Process -FilePath powershell.exe -WindowStyle Hidden -ArgumentList @('-NoProfile','-File',('"'+$cleanupScript+'"')) -PassThru -ErrorAction Stop
 $record.cleanup_pid=$cleanup.Id
 for($attempt=0;$attempt -lt 10;$attempt++) {
  if(Test-Path -LiteralPath C:/xwn657/firewall-cleanup-ready.json){break}
  if($cleanup.HasExited){throw 'Cleanup helper exited before readiness'}
  Start-Sleep -Seconds 1
 }
 if(!(Test-Path -LiteralPath C:/xwn657/firewall-cleanup-ready.json)){throw 'Cleanup helper not ready'}
 $ready=Get-Content -LiteralPath C:/xwn657/firewall-cleanup-ready.json -Raw | ConvertFrom-Json
 if($ready.pid -ne $cleanup.Id){throw 'Cleanup helper identity mismatch'}
 $record.expires_utc=[DateTime]::UtcNow.AddMinutes(10).ToString('o')
 Write-Output 'XWN657 receiver rule verified; automatic removal within 10 minutes. No Xbox launch was sent.'
} catch {$record.passed=$false;$record.failure=$_.Exception.Message;Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue;throw} finally {$record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $outPath -Encoding UTF8}
