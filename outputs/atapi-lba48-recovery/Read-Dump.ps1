#requires -Version 7.4
$ErrorActionPreference='Stop'
$k=$PSScriptRoot
$ws=Split-Path -Parent (Split-Path -Parent $k)
$out=Join-Path $k recovery003
$a=Get-Content (Join-Path $out audit.json) -Raw | ConvertFrom-Json
if (!$a.recovery_qualified -or $a.saved_dumps.Count -ne 1) { throw 'Cold recovery gate required' }
$report=Join-Path $out dump-reader.json
$log=Join-Path $out artifacts/cdb-recovered.txt
if ((Test-Path $report) -or (Test-Path $log)) { throw 'Reader attempt exists' }
$dump=Join-Path $out ('artifacts/'+$a.saved_dumps[0].artifact)
$cdb=Join-Path $ws work/microsoft-dump-reader/amd64/cdb.exe
$provenance=Get-Content (Join-Path $k dump-reader-provenance.json) -Raw | ConvertFrom-Json
$readerHash=(Get-FileHash -LiteralPath $cdb).Hash.ToLowerInvariant()
if ($readerHash -ne $provenance.files.'amd64/cdb.exe') { throw 'Reader identity changed' }
$signature=Get-AuthenticodeSignature -LiteralPath $cdb
if ($signature.Status -ne 'Valid') { throw 'Reader signature invalid' }
$symbols=Join-Path $ws work/microsoft-dump-reader/symbols
if (!(Test-Path $symbols)) { throw 'Empty local symbols directory required' }
$commands='.bugcheck; .dumpdebug; r; lm m *atapi*; lm m trigger; q'
& $cdb -sins -y $symbols -z $dump -c $commands -logo $log
$code=$LASTEXITCODE
@{exit_code=$code;commands=$commands;dump_sha256=(Get-FileHash $dump).Hash.ToLowerInvariant();
 log_sha256=(Get-FileHash $log).Hash.ToLowerInvariant();reader_sha256=$readerHash;
 authenticode=[string]$signature.Status;signer=$signature.SignerCertificate.Subject;
 symbols='existing empty local directory; no forced mismatched symbols';
 limits='Header, identity, register context and module-list validation; no complete stack-unwind claim.'} |
 ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $report
if ($code -ne 0) { throw 'Dump reader failed' }
