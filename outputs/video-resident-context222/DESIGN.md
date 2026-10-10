# Native resident context prefix222

Implement actual NT5 CPU ownership before connecting215's planner to GPU state.
One resident demand-loaded diagnostic driver owns a16KiB contiguous UC allocation
below the retained framebuffer reservation. All page starts/ends are translated
and validated, FileObject ownership and nonzero monotonically increasing tokens
are serialized by a real bounded NT5 mutex wait, and allocation failures consume
tokens rather than reuse them. Counter diagnostics saturate. Initial source and
destination guards, unused command storage and cleared future completion word are
checked byte-for-byte before query/exposure refusal/release. No command is built.

EXPOSE always returns HOLD: the runtime has no genuine instance/channel handoff.
There are no mock proof flags, GPU mappings/reads/writes, DMA descriptors, hardware
acknowledgements or channel borrowing. Returning actual translated CPU allocation
addresses for diagnostics does not make them GPU capabilities. CPU-only cleanup
is safe before exposure and is explicitly not completion or GPU drain evidence.
The module has no unload callback and remains resident until normal reboot.

The allocation retains its actual FileObject until release. Failed cleanup mutex
entry cannot leave a recycled owner address: a work item reserved on handle create
queues the pending cleanup IRP, retains another FileObject reference, and makes at
most eight further two-second waits at PASSIVE_LEVEL. Exhaustion returns failure
and retains the bounded CPU allocation/owner until reboot; it never frees memory
while contended or admits a new owner. This is CPU failure retention, not GPU
drain/quarantine. Normal workload validation does not exercise this rare native
fallback. Host callbacks test failed cleanup entry, retained ownership, foreign
cleanup rejection, subsequent successful cleanup and exact reference balancing.

The fresh probe uses distinct actual device handles: wrong-owner, stale-token and
short-request refusals, actual handle cleanup, then four bounded/joined concurrent
workers performing64 leases. Every successful lease has real translated ranges,
query and explicit exposure refusal before release. Final65 allocations/releases,
65 exposure refusals, one cleanup release and3194880 verified bytes are required.
No test-only kernel fault injection or token reset exists. Host-only callback
mocks additionally exercise translation/OOM/IRQL/lock failure, high-address
overflow, corruption, generation exhaustion and512 contended leases under
ASan/UBSan. These test the production CPU manager, not hardware witnesses.

Use a NEW unique ordinary emulator fixture from211, with reviewed219 candidate
bootvid and physical-core device policy unchanged. Pin actual native imports,
resident sections, helper/driver/fixture/source and run output. Keep221/older
closed cases untouched. Normal restart, exact logs, full cold allocation, five
hive structures, protected hashes/startup and unchanged event gates are required.
Inherited Ftdisk49 remains a strict whole-boot failure, not a waived event.

No physical deployment or device-thread merge. Preserve0101/video0093,0088rollback
and immutable0.1.0. Actual loader-to-NT5 instance/channel ownership, native GPU
context service/drain/quarantine, cache/completion and16x8 copy remain next steps;
this CPU ownership prefix alone authorizes none of them. SetMode TRUE runtime
guard coverage remains separate from221's actual SetMode FALSE crash guards.
