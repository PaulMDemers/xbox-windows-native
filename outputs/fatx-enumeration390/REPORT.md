# FATX cached enumeration cursor candidate390

Exact installed0101 source reproduced repeated exact-name results in388 host
checks and389 ordinary emulator control. Cached FCB indices store physical slots;
nonroot FATX directory enumeration adds two synthetic dot entries. The fast path
compared using logical indices but returned physical ones, so the next query
could select the same cached file again. The patch adds two to both returned
indices only for nonroot FATX; FAT and root paths stay unchanged.

Fresh pinned RosBE build001 reconstructed tree dc942ab4b23df76a2015c466dc37f97699938772.
Driver SHA256 41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126.
167827 bytes; checksum, i386 native subsystem and unchanged0101 imports verified.
Shared source working tree untouched.708 ASan/UBSan branch tests in388 are host
models, separate from runtime389 reproduction. Candidate runtime391 pending.
Physical console remains original0101; no broader filesystem qualification.

Closed392 now passes the matched exact-name/byte/audio/GDI/integrity scope.
See pair-review.json: original389 repeated32entries; corrected392 exactlyone.
Strict stillFALSE soleFt49. ActualCMD regression393 and hardware remain separate.

Closed393 actualNT5 CMD now passes original385 sixoperations and exact persisted
bytes alongside386 API/audio/GDI/coldintegrity. Hardware remains untested390.
