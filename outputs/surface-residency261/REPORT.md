#261 — complete guest pixel oracle; strict diagnostic still fails

This new emulator-only probe locks its own first4096-byte image/header page with
checked VirtualLock before entering the existing five-checkpoint protocol.007 had
proved that this header could be nonresident. No renderer or native driver changed.
Native compiler/import/export/callsite checks pass; all65536 independent expected
bytes,10 oracle mutations and26 complete synthetic attestation checks pass.

The single fresh launch completed all five actual native attestations and all four
real renderer stages. It used actual IDTR/trap-derived kernel identity, matching
kernel/probe/driver instructions, process/handle/FileObject ownership and all four
physical page translations at every stop. No debugger guest memory/register write
or dirty-arena read was used. Both CPU-exclusive callback inventories acknowledged
each stage; unknown vertex references remained zero. Frontend close/reopen and all
breakpoint/physical-read-mode teardown completed.

The actual guest verified four exact16384-byte reads: pattern0 after dirty age
removal, pattern1 through the real CPU-read callback, latest CPU seed after the
blocked write/eviction, and a second read checking for late stale data. Each read
covers572 pixel bytes plus15812 guard/padding bytes. Cold result.log contains all
four exact records and COMPLETE_RENDERER_PROTOCOL65536; counters are4reads/1write.
The inherited224 workload also completed64leases/65allocations/releases/refusals,
3194880 verified bytes,128 preflight reads and four joined workers.

Windows requested normal restart and returned to dashboard. Cold audit:322
directories,6728files,323directory clusters,zero errors/orphans,5structural hives
and31protected hashes. Integrity passes. The full run is CLOSED21:04:30UTC.

## Failures retained

The independent full preservation proof FAILS because CPU-read scalar telemetry
hit its256-event limit. The uncapped raw244 stream separately proves both actual
callback insertion/unlink/free lifetimes; it does not erase scalar truncation.
The original failing proof is preserved alongside supplemental observations.

The host runner's orderly close helper was absent from the copied260/261 kit.
After normal Windows shutdown/dashboard return, the runner fell back to killing
xemu (exit-1). This is a host-closure failure, even though guest persistence passed.
Inherited Ftdisk49 also remains a strict event failure. No gate is waived; no full
pixel-preservation qualification, ordinary result, speedup or physical promotion.

The original261 preflight rejected raw source SHA differences caused solely by
LF-to-CRLF copies. That writer/failure is preserved; the corrected preflight records
both hashes, normalized-source equality and identical compiled expected bytes.
Fresh1850-input manifest has exclusive review output and remains unchanged.

Physical audio004/softwarevideo118/shared158/FATX0101, immutable0.1.0,0088 and
private recovery256 remain unchanged. Historical250/258 fixture policies remain
explicitly separate from the audio-integrated physical demo.
