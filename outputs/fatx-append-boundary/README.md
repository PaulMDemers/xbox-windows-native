# Serial append boundary diagnostic

Emulator-only investigation of the physical GPU setup log anomaly. The physical
first-boot log contains a 111-byte damaged prefix at file offsets 270225..270335,
ending at both a 512-byte sector boundary and a 4096-byte page boundary. The cause
is unknown. The second physical boot preserved that prefix and appended ASCII
without another malformed span. Those physical records are not changed here.

## Workload

One original NT5 helper creates 96 exclusive files, one seed and one append each:

- Starting lengths 401,3985,65425,270225 bytes.
- Append lengths 110,111,112,219,221,4097 bytes.
- Same read/write handle; reopened generic-write handle; reopened write-through
  handle; reopened FILE_APPEND_DATA-only handle.

The append-only handle is closed and reopened with GENERIC_WRITE for the final
explicit FlushFileBuffers. Each seed is flushed before its append. All calls are
synchronous. The helper verifies source bytes/checksums, returned byte counts,
file length and every byte after closing and reopening. FNV32 values in the log
are diagnostics, not cryptographic identity. Cold audit independently generates
all expected bytes and records SHA256. The output directory must contain exactly
96 payload files and one complete log. The host requires normal guest shutdown,
one dashboard return, five parseable system hives, full F allocation consistency,
unchanged pinned payloads and strict event deltas. Existing byte-identical SCM7000
and Ftdisk49 records inherited from this emulator are classified explicitly;
Srv warnings, popups and application errors are not waived.

## Provenance and execution

Build.ps1 uses the pinned RosBE compiler under the shared build lease. review.py
checks imports against owned NT5 exports and records source, compiler and binary
hashes. prepare-fixture.py adds only helper/startup to a private child of the
immutable fatx-directory-order001 pre-run fixture, preserving 0101/video0093 and
all inherited hives. Historical emulator failed-install flags and placeholder
bindings remain; this is not physical first-install equivalence.

For each unique case 001 then002: prepare-fixture.py, Run.ps1, supervise.py,
trial.py collect, qualify.py. The supervisor uses only localhost4596 and launches
exactly once. It requests owned runner cleanup only after observing dashboard
return. Collection requires cleanup before read-only NBD access. A second case
requires first-case qualification. Completed attempts and reports are retained.
No debugger, guest mutation, raw guest disk write, physical FTP or new driver.

## API references and limits

Microsoft documents that FlushFileBuffers requires GENERIC_WRITE:
https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers
FILE_APPEND_DATA-only handles append at EOF:
https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntwritefile
Explicit flushing and application buffer lifetime:
https://learn.microsoft.com/en-us/windows/win32/fileio/flushing-system-buffered-i-o-data-to-disk
These contracts informed the helper; actual NT5 export and runtime validation
remain separate evidence.

This is a bounded serial test with deliberate flushes. It does not reproduce
concurrent SetupAPI activity, missing flushes, an interrupted first install,
physical timing or all cache-manager paths. Passing cannot identify or exclude
the cause of the physical log anomaly, and is not release qualification.
