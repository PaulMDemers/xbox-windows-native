# Next: establish instance backing and bounded context acquisition

216 is CLOSED. Read REPORT.md, state-observations.json, evidence-review.json,
emulator-pair-review.json and both actual host/closure records. Never relaunch
or recollect 216 or older closed cases. There are no owned running sessions.

The actual context is invalid, FIFO channel 1 differs from PGRAPH channel 0,
and hardware context switching is disabled. The exact xemu implementation
therefore requires the software context-switch path for a request. Do not
enable hardware switching, reset globally, clear IRQs or write a context merely
to obtain a PASS. The future native adapter needs an explicit bounded ownership
transition and service/drain path; the 215 witness flags do not implement it.

First pin the actual instance-memory allocation/backing contract. A useful
discriminator is the owned stock Xbox kernel's MmClaimGpuInstanceMemory
implementation and the loader memory ranges, rather than another unbounded
register sample. Inspect exact privately owned binary identity, export and
bounded implementation bytes before designing any runtime diagnostic. That
Xbox-kernel API is not an NT5 export and does not itself preserve a grant across
Xromwell. Distinguish physical UMA backing from xemu's separate RAMIN storage;
the NV04-family 512 KiB convention is only a lead. No boot buffer relocation or
new instance range is authorized by the current evidence.

Then specify one serialized NT5 context, its owned byte ranges and teardown:
validated PRAMIN/USER resource mappings, 213-style translated resident command
storage, software context-switch handling, bounded completion identity and
drain, timeout quarantine, crash/display handoff and allocation lifetime.
Retain the 215 generation/token binding and verify actual provider imports and
resident compiler output. Reject unsupported model methods and never turn
timeout into completion or reuse a quarantined allocation.

Only a concrete reviewed contract justifies a NEW unique emulator child for a
single guarded 16x8 copy outside scanout. Require exact pixels/guards, genuine
completion/drain, normal shutdown, full cold allocation/hive/protected audits
and unchanged strict event gates. Ftdisk 49 remains a strict failure on this
captured parent; scoped diagnostics do not silently waive it.

Keep physical0101/video0093,0088rollback,immutable0.1.0 and all failed evidence.
No device-thread integration or physical deployment follows from 216. Inspect
actual capacity before building; the 20 GiB guard is unchanged and C: is close.
Never casually relocate backing chains.
