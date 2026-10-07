# Repeated append persistence diagnostic

This owned emulator test follows the two passing single-append boundary runs.
It changes the helper and startup only, preserving FATX0101, video0093 and the
same immutable, already-installed GPU parent. No physical-console actions.

Each run creates16 exclusive files in C:\xwnas01. Four seed lengths (401,3985,
65425,270225) are combined with two flush policies and two handle lifetimes.
Each file receives512 synchronous appends, cycling through219,110,111,112,221
and4097 bytes. Every record ends in CRLF and has position-dependent ASCII bytes.
The first219-byte append at270225 covers the original111-byte damaged prefix
plus108-byte suffix. Contents depend on seed index and record number, making
the same-offset files identical across flush and handle policies.

Policy0 explicitly flushes after every append. Policy1 flushes only after all
512 appends. Both first flush the seed. Handle mode0 keeps the handle open;
mode1 closes/reopens before each append. These are cached generic read/write
handles positioned at EOF; no append-only or write-through semantic claims.
The closed/reopened mode may itself cause cache activity. The end-only policy
means no explicit per-append flush, not a promise that the cache never writes.

There is NO diagnostic log I/O inside the append loop. Source-byte validation,
returned write counts and cumulative source checksums are checked in memory.
Only after the selected final flush and close does the probe log the aggregate,
reopen/read and compare every byte. This reduces one timing perturbation; it
is still an instrumented, bounded serial test with no deliberately concurrent writers to its probe files.

The cold audit independently regenerates all16 expected files (not by trusting
live checksums), requires an exact output directory, source/completion records,
normal shutdown/dashboard return, reviewed binary hashes, five parseable hives,
unchanged prior event records and full F allocation consistency. Known identical
historical HID SCM7000/Ftdisk49 are classified explicitly; new errors, Srv
warnings, popups and application events are not waived. Old physical failures
remain separate. A PASS does not establish first-install or physical stability.

Build.ps1 and review.py pin RosBE, NT5 imports, source/build and binary hashes.
For unique cases001 and002: prepare-fixture.py, Run.ps1, supervise.py, then
trial.py collect and qualify.py after owned cleanup. Case002 requires001PASS.
Each uses an independent child of the same original parent, never a prior test's
output. The localhost FTP supervisor launches only once. No debugger or forced
shutdown belongs to a passing run. Private disks and artifacts stay ignored.
Git retains exact source/report bytes for their SHA256 references.
