# Persistent, explicitly user-authorized rule for one development Xbox.
param(
 [ValidateSet('Install','Remove','Verify')][string]$Action='Verify',
 [string]$Configuration='C:\xwn-network\firewall.json',
 [Parameter(Mandatory=$true)][string]$Receipt
)
$ErrorActionPreference='Stop'
if(Test-Path -LiteralPath $Receipt){throw 'Receipt already exists; choose a fresh receipt.'}
$record=@{passed=$false;action=$Action;utc=[DateTime]::UtcNow.ToString('o');persistent=$true;rule='XWN-DevelopmentXbox-UDP50657';program_filter='Any';local_port=50657}
try {
 $cfg=Get-Content -LiteralPath $Configuration -Raw -ErrorAction Stop | ConvertFrom-Json
 $peer=[System.Net.IPAddress]::Parse($cfg.console)
 $hostAddress=[System.Net.IPAddress]::Parse($cfg.host_address)
 if($peer.AddressFamily -ne 'InterNetwork' -or $hostAddress.AddressFamily -ne 'InterNetwork' -or $cfg.port -ne 50657){throw 'Unexpected configuration'}
 $iface=(Get-NetIPAddress -AddressFamily IPv4 -IPAddress $cfg.host_address -ErrorAction Stop).InterfaceAlias
 $existing=Get-NetFirewallRule -Name $record.rule -ErrorAction SilentlyContinue
 if($Action -eq 'Remove'){
  if($existing){$existing | Remove-NetFirewallRule -ErrorAction Stop}
  if(Get-NetFirewallRule -Name $record.rule -ErrorAction SilentlyContinue){throw 'Rule remains'}
  $record.removed=$true
 } else {
  if($Action -eq 'Install' -and !$existing){
   New-NetFirewallRule -Name $record.rule -DisplayName 'Xbox development diagnostic UDP (one console)' -Description 'User-authorized persistent inbound UDP50657 from the configured development Xbox on its LAN interface. No timer. Remove using Set-XboxDiagnosticFirewall.ps1 -Action Remove.' -Direction Inbound -Action Allow -Enabled True -Protocol UDP -LocalPort 50657 -RemoteAddress $cfg.console -InterfaceAlias $iface -Profile Any -EdgeTraversalPolicy Block -PolicyStore PersistentStore -ErrorAction Stop | Out-Null
   $record.created=$true
  }
  # Inspect effective policy as well as persistence. Never widen/replace a conflicting rule.
  foreach($store in @('PersistentStore','ActiveStore')){
   $r=Get-NetFirewallRule -Name $record.rule -PolicyStore $store -ErrorAction Stop
   $p=$r|Get-NetFirewallPortFilter; $a=$r|Get-NetFirewallAddressFilter; $i=$r|Get-NetFirewallInterfaceFilter; $app=$r|Get-NetFirewallApplicationFilter
   if($r.Enabled -ne 'True' -or $r.Action -ne 'Allow' -or $r.Direction -ne 'Inbound' -or $p.Protocol -ne 'UDP' -or $p.LocalPort -ne '50657' -or $a.RemoteAddress -ne $cfg.console -or $i.InterfaceAlias -ne $iface -or $app.Program -ne 'Any' -or $r.EdgeTraversalPolicy -ne 'Block'){throw ('Exact rule mismatch in '+$store)}
  }
  $record.effective_and_persistent_verified=$true
  $record.scope='Inbound UDP50657 from configured development Xbox only, resolved LAN interface, any profile/program. No firewall disable or general port range.'
 }
 $record.passed=$true
 Write-Output ('Xbox diagnostic firewall action completed: '+$Action)
} catch {$record.failure=$_.Exception.Message;throw} finally {
 $record.finished_utc=[DateTime]::UtcNow.ToString('o')
 $record | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $Receipt -Encoding UTF8
}
