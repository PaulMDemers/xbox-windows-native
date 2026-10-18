# Closed executable storage523

Seven separately owned closed xemu executable copies were losslessly compressed
in place, preserving every original byte, path, length, file identity and link
count. They belong to502/505/507/511/512/513/517; each was joined to its own instance,
final-review, successful host-exit and cleanup record. Failed511/512 runtime results
remain failed. No closed runtime was rerun or recollected.

Logical bytes1339219399; actual FILE_STANDARD_INFO allocation before1339240448,
after687984640. Recovered651255808 bytes (621.09MiB), using one bounded explicit
compact.exe /C /I /Q call, exit0. Allseven compressed. Independent standard-library
hashing and Win32 allocation/identity readback passed. No file was deleted, moved,
replaced or semantically edited. Shared installed emulator, backing chains,
firmware/EEPROM, snapshots521, recovery256 and console were untouched.

Read-only plan001 FAILED because its new streaming hash helper returned a hash
object rather than its hex digest. Nothing was compressed at that point. Original
source/result are preserved; common002 corrects only the return conversion.
Plan002 and apply001 passed. No compressor failure or retry occurred.

Review Cfree22870188032/E21499871232 bytes. The unchanged768MiB projected
preparation plus20GiB floor passes with590045184 additional bytes, also exceeding
the512MiB operational headroom target. Later preparation still rechecks capacity.
No E allocation. All owned storage/review subprocesses closed; Windows/WSL
inventories found no emulator. No build, guest preparation/launch, physical access
or hook occurred.520 remains never launched;522 host qualification stays separate.

Evidence: plan001-failure.md, plan002.json, apply001.json, review001.json,
final-review.json. Public repository retains only source/metadata, no binaries.
