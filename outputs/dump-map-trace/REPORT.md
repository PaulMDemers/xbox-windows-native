# Runtime dump mapping matches the independent disk oracle

2026-10-07. The unique trace001 diagnostic is CLOSED. Its launch at 10:46:19
UTC returned to the dashboard at 10:48:33. No physical console was accessed.
This debugger result is distinct from the prior ordinary FATX0103 comparison.

Eighteen paired runtime events and 25 relocated resident-byte pins identify
the actual candidate0103 FATX, candidate0102 HAL and owned NT5 kernel. Dump
usage notification, disk-stack setup, file reference, standard-information
query, FATX dispatch, FSCTL return and final initialization caller all succeed.
The actual request is KernelMode 0x9003b, eight-byte input containing 65536,
and a four-byte output pointer slot. Its successful IOSB is (0,4).

The output points to nonpaged array 0xfe4f83c8. Its first pair is byte length
65536 and volume-relative byte offset 140436013056, followed by a zero pair.
This matches the independently read cold FAT chain exactly. The final kernel
dump context retains the same pointer, requested length 65536 and mapping
size 24 bytes (length, offset and terminating zero length). Three separately
pinned consumer windows substantiate those field interpretations. The full
32-byte returned array includes the final zero offset as well.

Every breakpoint was removed, no call remained pending, and the guest resumed.
The standard workload then completed 792 appends, 32 allocation shrinks and
132 reopens. All 11 cold files match exact expected bytes. Full allocation is
consistent: 323 directories, 6765 files, 324 directory clusters, zero errors
or orphan clusters. Five hives parse, protected hashes/payloads match, normal
shutdown is recorded, and no new warning/error or application events occur.
The strict diagnostic audit passes. Ordinary qualification remains explicitly
false for this debugger run; the prior ordinary candidate comparison passed.

Dump configuration remains enabled and unchanged. The 96 MiB pagefile's 1536
clusters and extent map match before/after. The first extent exceeds 128 GiB.
No actual crash dump was written or recovered here; miniport large-LBA writes
and post-crash recovery remain unqualified. The original physical 111-byte
non-ASCII corruption and first restart method are still unresolved.

`trace-verification.json` replays the raw pins, paired frames/threads, buffers,
retained context, independent before/after maps and audit. Frozen source and
input hashes, private disk closure hash and raw cold evidence also verify.
No driver/settings/policy changes or qualification waivers were made in this
kit. Inherited emulator-only synthetic null/unsupported devices remain explicit.
