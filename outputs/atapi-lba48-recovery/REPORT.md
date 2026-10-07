# Separate high-LBA dump recovery passed

Recovery003 booted once at2026-10-07 15:37:39UTC and returned to the dashboard
at15:39:09UTC after one normal shutdown. Windows created
C:\WINNT\Minidump\Mini100726-01.dmp. All65,536 bytes exactly match the
original controlled-crash payload; SHA256
5ea3efb2a21c93fd6dd06411aa0344d2a4e74c02cc99863df636f989795da370.
The original crash006 image and its backing chain remain unchanged and were
never booted. Recovery used a separate writable child only.

Full allocation:326 directories,6760 files,327 directory clusters, zero errors
and orphans. Five structural hives, protected files, recovery helper and startup
hashes passed. Existing event history survived, with the expected informational
Save Dump1001 carrying the exact bugcheck/cookie/path, one normal shutdown,
no warning/error delta and no application delta. Pagefile cluster map and dump
configuration remained unchanged. No service, dump setting or event was suppressed.

Microsoft's signed CDB10.0.29661.1004 independently opened the saved file as a
Windows2000SP4 x86 kernel minidump. It read the exact bugcheck/parameters,
64KiB triage structure, register context and ATAPI/dump_ATAPI/trigger modules.
Missing legacy extensions and absent symbols are retained in the private reader
log; full symbolic stack unwinding is not claimed. Tools were extracted privately
from the official Microsoft bundle without installation. Provenance and hashes
are recorded; no Microsoft binary or dump is committed.

See verification.json, recovery003/audit.json, dump-reader.json and closure.json.
This establishes one controlled emulator dump and recovery, separate from the
ordinary matched storage/network PASS. It does not qualify physical hardware,
general crash resilience or disk addresses beyond the upstream32-bit LBA limit.

## Preserved host failures

Recovery001 failed before guest boot because its backing path used WSL's /mnt/c.
Recovery002 failed before guest boot with a nested relative backing path that
Windows xemu could not open. Both run disks exactly matched unbooted seeds;
no Windows launch was requested. Neither attempt was relaunched.
Recovery003 uses a copied28MB crash overlay alongside its existing parent.
Only that copy's backing pathname changed; qemu-img compare confirmed complete
logical-disk equality before preparation. Original images were never modified.
Its preflight also rejected an accidental CRLF change to the build script;
restoring the exact pinned source resolved it before any run directory/guest.
All failure records and frozen sources remain available.
