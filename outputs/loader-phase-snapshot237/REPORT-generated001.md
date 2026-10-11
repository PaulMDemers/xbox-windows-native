#237 independent GPU snapshots at loader boundaries

Three independent debugger runs used one fresh immutable seed and three unique writable copies. Unchanged234 emulator and224/219/211 native fixture. No physical access, driver changes, device integration or release tag changes. CPU-stopped PG worker observations; no ordinary accelerated-driver qualification.

| Independent case | CPU phase EIP | Snapshot | Pending | Wait flags | Trace / CPU / cold integrity |
|---|---:|---|---:|---|---|
| dashboard001 | 0x146677 | state3 | 0x100000 | NOP | True / True / True |
| xbe001 | 0x11100 | state3 | 0x0 | none | True / True / True |
| freeldr001 | 0x200a20 | state3 | 0x0 | none | True / True / True |

Each loader stop matched owned cold executable bytes. Xromwell entry11100 and FreeLoader multiboot200a20 are actual executing stops; magic2badb002/IF0 at FreeLoader. Dashboard is arbitrary CPU stop, unlike prior mid-IRQ acknowledgement. These are independent boots, not a simultaneous single-boot timeline.

Published tuples reread byte-identically. Current PG row FIFO-valid0: historical valid journal rows do not establish current DMA GET/PUT. Worker can progress while CPU stopped. Compiled wait bits1FIFO access disabled,2NOP,4flip,8context switch. No flag silently cleared.

dashboard001: publication passedTrue; journal total17640/count256/overwritten17384, lost prefix retained. Normal shutdown1/dashboardTrue; allocation{'directories': 320, 'files': 6725, 'directory_clusters': 321, 'orphan_cluster_count': 0, 'errors': []}; five structural hives. Warning/error deltas[{'source': 'Ftdisk', 'event_id': 49, 'type': 1}]. Strict/ordinary/physical GPU qualification FALSE.
xbe001: publication passedTrue; journal total22717/count256/overwritten22461, lost prefix retained. Normal shutdown1/dashboardTrue; allocation{'directories': 320, 'files': 6724, 'directory_clusters': 321, 'orphan_cluster_count': 0, 'errors': []}; five structural hives. Warning/error deltas[{'source': 'Ftdisk', 'event_id': 49, 'type': 1}]. Strict/ordinary/physical GPU qualification FALSE.
freeldr001: publication passedTrue; journal total19522/count256/overwritten19266, lost prefix retained. Normal shutdown1/dashboardTrue; allocation{'directories': 320, 'files': 6724, 'directory_clusters': 321, 'orphan_cluster_count': 0, 'errors': []}; five structural hives. Warning/error deltas[{'source': 'Ftdisk', 'event_id': 49, 'type': 1}]. Strict/ordinary/physical GPU qualification FALSE.

Unchanged CPU regression requires65 allocations/releases/exposure refusals,3194880 verified bytes/four joined workers; actual per-case results are shown above. Eight MMIO retirement rounds/128 sequential reads are required to refuse UNMODELED_BUSY/NO_OWNERSHIP. No renderer-reference retirement, dirty-surface readback, alias coherence, instance allocation or native permit proven.

Host tests57 actual sampler/parser checks,72 helper guards,12 actual supervisor connection checks; PowerShell syntax/prelaunch review passed. Initial parser rejected producer kind1, caught on preserved236 raw evidence before launch and retained in parser-preliminary001-failure.json; corrected using actual journal-kind evidence. No guest replay.

All470 frozen pins unchanged. Actual resident pins/raw immutable tuples reviewed; breakpoint removals/mode0/resume/closure recorded. Every new runtime cold-audited exactly once.

Closure caveat: inherited host runner uses vm.Kill after capture. Cold evidence is recovered-image allocation/hives/selected-content scope, not all-file-content durability, completed emulator cache flush or repeated boots. USB peer cda0476 isolated forced-exit mapping loss versus orderly closure on its own fixture; no silent closure change in this frozen matrix. Physical0101/video0093,0088rollback,immutable0.1.0 untouched.

Read review001.json/prelaunch-review001.json/matrix001.json and each trace.json/audit.json/closure.json plus DESIGN.md for actual scope.

Both executing loader-entry samples have no pending PGRAPH interrupt and no wait flags. This does not support diagnosing a persistent PGRAPH wait at those sampled transfers from the earlier dashboard stop. It does not establish FIFO drain, producer admission close, renderer-reference retirement or complete GPU idle. The next discriminator is current FIFO and referenced context/surface lifetime, not forced wait clearing.
