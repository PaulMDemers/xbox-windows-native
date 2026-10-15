$ErrorActionPreference = 'Stop'
$base = 'E:\xwn329\retained-builds001\xemu-hd322.exe'
$target = 'E:\xwn405\instances\windows-native-fresh405-emu001\EA3473314E6C0EA0\xemu-windows-native-fresh405-emu001.exe'
$receipt = Join-Path $PSScriptRoot 'deduplicate001.json'
if (Test-Path -LiteralPath $receipt) { throw 'Consumed ID' }
if (Get-Process xemu* -ErrorAction SilentlyContinue) { throw 'Emulator active' }
$base = (Resolve-Path -LiteralPath $base).Path
$target = (Resolve-Path -LiteralPath $target).Path
if (-not $target.StartsWith('E:\xwn405\instances\') -or $base -eq $target) { throw 'Unexpected path' }
$expected = 'EA3473314E6C0EA068DE4202CDE46B1405DA7553240CADEA738C29C16D74C7A3'
$a = Get-FileHash -LiteralPath $base -Algorithm SHA256
$b = Get-FileHash -LiteralPath $target -Algorithm SHA256
if ($a.Hash -ne $expected -or $b.Hash -ne $expected) { throw 'Not identical retained executable' }
$size = (Get-Item -LiteralPath $target).Length
$record = @{source=$base;target=$target;sha256=$expected.ToLower();bytes=$size;status='verified-before-replacement';scope='Only duplicate closed emulator executable; original path retained as NTFS hard link; no disk/backing-chain mutation'}
$record | ConvertTo-Json | Set-Content -LiteralPath $receipt
Remove-Item -LiteralPath $target
New-Item -ItemType HardLink -Path $target -Target $base | Out-Null
if ((Get-FileHash -LiteralPath $target).Hash -ne $expected) { throw 'Readback mismatch' }
$record.status='hardlink-readback-verified'
$record.free_bytes_after=(Get-PSDrive E).Free
$record | ConvertTo-Json | Set-Content -LiteralPath $receipt
$record | ConvertTo-Json
