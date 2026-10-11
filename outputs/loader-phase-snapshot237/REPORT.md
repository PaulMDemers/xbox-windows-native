# GPU state at the loader boundaries

Three independent emulator runs captured one immutable GPU snapshot each, with the CPU paused at the dashboard, Xromwell entry, or FreeLoader entry. They used a fresh shared immutable seed, separate writable disks, and unchanged emulator234 and native224/219/211 payloads. The physical Xbox and release0.1.0 were untouched.

Both executing loader entries had zero pending PGRAPH interrupts and zero wait flags. The earlier dashboard NOP observation does not establish a persistent wait at these sampled transfers. Current FIFO state, producer admission, referenced contexts/surfaces, dirty readback, and safe GPU ownership still need evidence.

| Independent run | CPU EIP | PGRAPH pending | Wait mask | Journal total / retained / overwritten |
|---|---:|---:|---:|---|
| dashboard001 | 0x146677 | 0x100000 | 2 (NOP) | 17640 / 256 / 17384 |
| xbe001 | 0x11100 | 0x0 | 0 (none) | 22717 / 256 / 22461 |
| freeldr001 | 0x200a20 | 0x0 | 0 (none) | 19522 / 256 / 19266 |

Each snapshot published successfully and reread byte-identically. Xromwell entry0x11100 and FreeLoader entry0x200a20 matched32 resident bytes from the owned binaries in every run. FreeLoader had multiboot magic0x2badb002 and interrupts disabled. Dashboard is an arbitrary CPU stop; the rows represent separate boots, not one simultaneous timeline.

The worker may progress while the CPU is stopped. Current tuples contain PGRAPH state only; FIFO-valid is zero. Historical valid FIFO rows cannot establish current DMA GET/PUT. Wait bits from the pinned compiled source are1FIFO access disabled,2NOP,4flip,8context switch. Overwritten journal prefixes remain unknown.

All three runs completed65 allocations, releases and exposure refusals, verified3,194,880 bytes, and joined four workers. Eight retirement rounds with128 MMIO reads retained UNMODELED_BUSY/NO_OWNERSHIP. Each run shut down normally and returned to the dashboard. Debugger points were removed, read mode remained zero, and all16 recorded root processes are absent. No memory/register writes or GPU command writes.

Cold checks passed complete allocation consistency, five structural registry hives, protected file hashes, startup, event/history continuity, and selected device policy. Counts were320 directories and321 directory clusters each; files6725 for dashboard and6724 for both entry runs, zero errors/orphans. Existing directory captures identify the extra dashboard file as /winnt/system32/wbem/logs/wmiadap.log; no baseline paths disappeared. This is path presence, not complete payload equality.

Every run retained Ftdisk49 as a strict error, with no new application events. Strict, ordinary and physical GPU qualification remain false. The host harness still forces emulator exit after capture: these cold checks cover the recovered image and selected content, not completed emulator cache flush or repeated-boot durability. USB peer cda0476 demonstrated forced-exit mapping loss versus orderly closure on a separate fixture; that procedure was not silently substituted in this frozen matrix.

Host validation passed57 actual sampler/parser checks,72 helper guards,12 actual supervisor connection checks,5 capture-parser boundaries, PowerShell syntax and prelaunch review. All470 frozen pins remained unchanged. Preliminary producer-kind and empty-directory parser mistakes were caught on existing captures, corrected from actual formats, and preserved. No closed run was replayed or recollected.

Next: observe current FIFO state and referenced context/surface lifetime at the verified entries, then select a bounded preservation experiment from those results. Separately review orderly emulator closure before claiming stronger durability. Physical0101/video0093, original0088 rollback, immutable0.1.0 and all failures remain preserved.

Evidence: review001.json, matrix001.json, prelaunch-review001.json, directory-delta001.json, process-closure001.json, and each runs trace.json/audit.json/closure.json. See DESIGN.md and NEXT.md for scope and continuation.
