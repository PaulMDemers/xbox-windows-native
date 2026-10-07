# Later interruption reproduces a file-visible111/109 split

Emulator-only debugger experiment,7October2026. Launch06:22:09UTC; checkpoint
06:25:25.380UTC; owned emulator exit0 and cleanup06:25:25.773UTC. Runner30331,
tracer13547 and supervisor88280 are all closed. The generic runner reports
exit1 with `Task emulator exited: 0` because HMP quit ends its owned emulator.

The selected request wrote1524 bytes starting at270336, including the exact109
target suffix. Its VfatWrite return was success with Information1524. All58
captured actual mapped log buffers are preserved. No observed write overlapped
the target111-byte prefix. The tracer removed all breakpoints at the accepted
return, confirmed `paused (debug)`, and sent HMP quit with GDB attached. It did
not resume, step or detach the guest. No target request remained pending.

Cold readback resolves this file's own FAT chain and finds:

| Evidence | Result |
|---|---|
| Persisted file size |271385 bytes; includes the entire target|
| Target offset |270225;4096-byte page offset3985|
| First111 bytes |Zero, unchanged from immutable input|
| Following109 bytes |Exact expected warning suffix|
| File versus raw disk |Exact agreement at the target|
| Full F allocation |Consistent; zero errors and orphans|
| Five hive structures |Parse; matching header sequence numbers|
| Normal shutdown |Absent, as intentionally prevented|

The unchanged normal-shutdown control `../../fatx-paging-buffer/002` contains all
220 warning bytes correctly, with the prefix page observed near shutdown. The
interrupted fixture therefore demonstrates that file length and later-page data
can persist before the earlier dirty page. Consistent allocation and valid hives
alone do not establish file-data durability.

**This is a boundary/mechanism reproduction, not the original physical failure.**
The hardware's111-byte damaged prefix contained non-ASCII data; this fixture's
prefix is zero. Physical first-write allocation history and first restart method
remain unknown. HMP host exit also differs from physical power loss. No driver
fix, ordinary stability PASS, physical qualification or release change follows.

Case002's recorder failure remains separate. Case003 uses the tested bounded
atomic replacement helper; its source hash is pinned in the trace. HMP's socket
reset is recorded explicitly as an exit disconnect, with independent process
exit0/cleanup evidence. Private raw buffers, logs, hives and overlay are retained.
Next confirm the application's actual mapped-append lifecycle, then use a
focused normal-shutdown regression before considering any functional changes.
