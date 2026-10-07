# Continue after the closed dump configuration diagnostics

All dump-config-trace serial001 through005 are CLOSED. Never relaunch/recollect.
Read REPORT.md, trace-verification.json and serial005/trace.json. Earlier
baseline-hid-restore ordinary pair also remains closed and strictly failed49.

Concrete path: IoGetDumpStack's IopSynchronousCall for PnP major1b/minor16,
InPath1/type3 fails STATUS_NOT_SUPPORTED. Disk queries and40-byte dump pointers
succeed; miniport dump driver loads successfully. Candidate0101 VfatPnp forwards
the request to Ftdisk and gets STATUS_PENDING. Final lower completion producer
is NOT identified. FSCTL_QUERY_RETRIEVAL_POINTERS is not reached; do not patch it
as the explanation for current49. The shared caller error block has multiple
incoming branches; the original whole-function assumption was wrong and the
serial001 failure is preserved. All five post-trace workloads/cold audits pass
integrity, but strict events remainFALSE, sole49. Debugger runs are distinct
from ordinary regression and physical results.

Next NEW isolated trace: record dispatch/completion of the same PnP IRP through
Ftdisk/lower disk/port objects, allow pending completion on another thread,
capture final IoStatus before deallocation, and pin actual loaded module bases
and resident bytes to the six cold-verified storage binaries. Do not trust
serial005 pointer addresses on a new boot. Kernel publics, pnp-layouts and
matching0101 COFF symbols are available. A short IofCallDriver/complete-request
window must be activated only around the identified usage request, with strict
IRP ownership, bounded captures and complete breakpoint removal. Do not infer
Ftdisk itself rejected it from its name at the filesystem handoff.

All current launch entry points address occupied case IDs. Use a NEW kit/ID
and source/fixture pins; no overwrite of prior records or use of completed
disks as fresh parents. No speculative driver patch, fake success, service or
dump disabling, event suppression or relaxed gate. Continue emulator-only until
13:00UTC October7, checking time first; at cutoff no new experiments, cleanup,
report and pause automation. No physical FTP/deploy/test. Preserve0101/video0093,
0088rollback,immutable0.1.0, all failed evidence and inherited emulator-only PnP
policy. Original physical111 non-ASCII damage and first restart remain unknown.
