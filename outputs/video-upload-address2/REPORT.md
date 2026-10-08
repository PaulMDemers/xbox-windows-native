# Same copy path and paging flags at all three positions

The bounded debugger diagnostic captured all three translated solid rectangles:
192x96 at (0,0), (128,0) and (0,160). It passed the independent trace verifier and
the full cold workload audit. This is diagnostic evidence only: ordinary and
timing qualification are explicitly false. No driver or emulator binary changed.

## Observed execution and mappings

There are 24 paired marker/call/copy/return events and 15 resident instruction
pins. All three first-row calls reach the same local memmove routine and forward
rep movsd loop. ECX starts at 192 dwords and ends at zero; ESI/EDI advance by 768
bytes. All 768 destination bytes equal the captured source. Both the copy and
whole-upload returns match their originating thread, process and stack. Each
upload adds exactly one upload and 73,728 bytes to the driver's counters.

Source-level memcpy resolves to a local linked memmove, not an imported function.
The reviewed display offsets are XwnUploadBox+0x0 (RVA0x27b0), call0x27fa,
memmove0x3f10 and rep movsd0x3f4d. Live display base was0xf8e00000. Code bytes,
relocations, COFF symbols and actual instruction operands corroborate PDEV fields.
Do not infer instructions used by every subsequent row from the first-row sample.

|Item|Observed value in all three samples|
|---|---|
|RAM shadow base|0xe1c00000|
|Framebuffer virtual base|0xfced6000|
|Source and destination pitch|4096 bytes|
|CR3|0x03985000|
|Source PWT / PCD / PAT|0 / 0 / 0|
|Destination PWT / PCD / PAT|1 / 1 / 0|
|Paging size|4 KiB pages on both sides|

Raw PDE/PTE snapshots cover both endpoints of all 96 rows on both sides of each
sample. Each row fits one page. The destination translates to0x03c00000 plus its
pixel offset: y160 begins at0x03ca0000. Each set has 96 unique source and 96 unique
destination physical pages, with no overlap between the source and destination
sets. Destination rows are physically contiguous; shadow rows are fragmented
(41/95 adjacent page pairs at the top, 33/95 at y160). Fragmentation is an
observation, not an established cause of the timing difference.

The page-table flags are identical across positions. This rules out a position-
dependent change in those recorded flags, not every effective cache-type effect:
PAT/MTRR state and xemu software-TLB behavior were not measured. Source and
destination shift together, so this does not isolate which side incurs the cost.

## Identity, failure preservation and limits

The first kit, video-upload-address, failed before collecting an upload because
the user loader-list pointer was unreadable. It removed its breakpoint, resumed
Windows, and later passed the cold workload. Its diagnostic-result.json remains
false. It was neither relaunched nor promoted based on the successful retry.

This fresh kit uses the kernel loader list for the display and identifies the
executing probe by its actual marker address, live PE header and resident bytes.
The display's PE header was unreadable (E14), as recorded; identity uses its
kernel loader name/base/size, exact relocated resident instructions and cold
binary hash. The live kernel was independently identified by two IDT gates and
its PE identity (base0x823e0000). No registers, page mappings or results were edited.

All breakpoints were removed and the guest resumed at05:26:40.695117UTC. The
observer was bounded to64 stops/600 seconds and used24 stops. Eight synthetic
corruptions of teardown, operands, page translations, flags, copy results, stack
pairing and row coverage are rejected. These tests are not guest evidence.

## Cold result and artifacts

The continuing workload completed 45 cases, 13,271,040 exact live pixels,
45 exact cold reference files and45 actual RGB readbacks; 86,528 measured BitBlt
callbacks match the protocol. Timing values are retained but excluded from all
performance qualification because this was a debugger run.

Normal shutdown and dashboard return; no warning/error or application event delta.
Complete allocation:327 directories,6851 files,328 directory clusters, zero errors
or orphans. Five structural hives, protected binaries, startup, configuration and
the96MiB/1536-cluster pagefile remain valid/unchanged under their existing checks.

Probe141 SHA2560e8e2f65c36ceb851df94fa1d389305b9ad4ce0e79c4c3b1800654e93a1ae1a6;
display0112 SHA256ba6e37ddb2bdaad05cc12585fe9c986bdb5203c94101443500ebf1c547c81da8.
The exact same probe and display were used in the failed and successful attempts.
Inherited emulator-only device policy, Shared-UC0106, FATX0103/HAL0102,
NVNet0104/ATAPI0105 and HidServ are unchanged. No physical FTP, deployment or test.
Physical0101/video0093,0088rollback and immutable0.1.0 remain preserved.

Preparation51131, runner6302, tracer80999, supervisor81307, audit90793 and
verifier96282 are CLOSED. Single launch accepted2026-10-08T05:25:44.530603UTC;
dashboard returned05:30:35.583805. Private disk:
work/runs/nt5-vaddress2-candidate001/hdd.qcow2, pinned in closure.json.
Never relaunch/recollect either closed diagnostic. C: last measured about21GiB
free; recheck before a fresh build and preserve the20GiB guard.

## Next discriminator

source-followup.json pins a more specific static emulator lead: GPU surface ranges
can register TCG CPU-access callbacks. The callback locks PGRAPH, searches surface
overlaps and may schedule a download; cputlb adds callback-match flags. Existing
nv2a_pgraph_surface_cpu_read/write events record surface base and offset.

This is not proof those callbacks occurred or caused the slowdown. A fresh bounded
trace should correlate these events with actual top/lower physical copy ranges,
using marker-delimited draws and a verified trace backend. Do not disable callbacks
or change the driver to force an improvement. Keep trace timings excluded; any
later change needs matched ordinary correctness and performance runs.
