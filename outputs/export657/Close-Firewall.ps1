# Elevated child of Open-Firewall.ps1; bounded cleanup of this one named rule.
$ErrorActionPreference='Stop'
$kitPath=Split-Path -Parent $MyInvocation.MyCommand.Path
$outPath=Join-Path $kitPath firewall-close002.json
$deadline=[DateTime]::UtcNow.AddMinutes(10)
$record=@{removed=$false;rule='XWN657-owned-UDP'}
try {
 if(Test-Path -LiteralPath C:/xwn657/firewall-cleanup-ready.json){throw 'Existing cleanup owner'}
 @{pid=$PID;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath C:/xwn657/firewall-cleanup-ready.json -Encoding UTF8
 while([DateTime]::UtcNow -lt $deadline -and !(Test-Path -LiteralPath C:/xwn657/close-firewall.request)){Start-Sleep -Seconds 1}
 Get-NetFirewallRule -Name 'XWN657-owned-UDP' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction Stop
 if(Get-NetFirewallRule -Name 'XWN657-owned-UDP' -ErrorAction SilentlyContinue){throw 'Rule remains'}
 $record.removed=$true
} catch {$record.failure=$_.Exception.Message;throw} finally {$record.utc=[DateTime]::UtcNow.ToString('o');$record | ConvertTo-Json | Set-Content -LiteralPath $outPath -Encoding UTF8}
