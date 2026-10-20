# PC618 closed PASS: matched saved-scene process costs

The matched recorder-cost milestone is complete. A fresh immutable404 child ran
19:13:32–19:22:41 UTC on 2026-10-20. It restored the same paused PC593 saved scene,
window geometry, cursor and five-second settling used by pristine PC615. All
165,600 scenery pixels matched the reference before timing and remained exact
afterward. Nine private screenshots were inspected; no blank/error frame or
rendering corruption was observed.

## Measured interval

| Process / condition | Guest elapsed | Process CPU | Share of one emulated CPU |
| --- | ---: | ---: | ---: |
| Pristine615 game | 20.016 s | 19.859375 s | 99.22% |
| Recorded618 game | 20.062 s | 19.312500 s | 96.26% |
| Recorded618 recorder | same interval | 0.375000 s | 1.87% |
| Recorded618 observer | same interval | 0.015625 s | 0.078% |

Independent host elapsed was20.044836489s for618, within17.164ms of guest ticks.
The same-boot five-second sleep matched4.995475535s host. QPC still misreported
elapsed time and was excluded from the measurement.176 samples used verified,
distinct actual game, recorder and observer process identities. Game working set
was stable35,971,072 bytes versus35,319,808 in615. Recorder working set ranged
1,052,672–1,056,768 bytes. PagefileUsage is an allocation counter, not disk paging
traffic. Exact values and source hashes are in comparison001.json.

The paused game dominates CPU time in both intervals. This establishes the
recorder process's measured CPU cost for this policy; it does not isolate all
instrumentation overhead imposed inside the game or operating system. One
interval per condition cannot establish a speedup, FPS, useful simulation work,
Xbox performance or GPU acceleration. Attribution of game CPU to waiting,
rendering and copies remains necessary before selecting an optimization.

## Recorder coverage

The byte-identical617 window and timing code starts counters/host marker before
requesting phase1 while the game continues running.32 phase1 sampled call/return
pairs lie inside the window.522 API11 entry ticks are strictly interior; one
endpoint-tick hit remains separate. Total phase1 hits1379 include post-window
execution during log writing and game close, so they are not a window count.
Phase0 recorded2495 hits. The32-pair cap leaves entry breakpoint handling active.
The result describes capped sampling plus ongoing entry handling, not a
continuous full-call recorder. The sampled StretchDIBits path is GDI; API counts
are not frames.

## Validation and preserved failures

Source/binary/media readback,11 counter rejection cases,10 copy rejection cases,
7 scene rejection cases,13 timestamp-alignment rejection cases, independent
host timing, raw event timestamps and cold validation passed. The corrected
alignment decoder produces an identical result on cached617 exports without
reopening that runtime.

The copy test was initially invoked before its media receipt existed; this
ordering failure is retained. Review001 rejected two valid pairs because it
incorrectly required separate entry/call GetTickCount reads to be equal. The
corrected decoder associates each of the first32 call IDs with its ordinal
entry and requires entry <= call <= return, with call no later than the next
entry. Both observed16ms differences meet this ordering. No runtime or frozen
source bytes changed. Review002 then failed a JSON-list/Python-tuple ROI
comparison; review003 compares JSON-normalized structures and passed. All failed
receipts, decoder versions and the explanation records remain preserved.

The guest exited normally, restored registry values and the exact save, and
recorded one normal EventLog shutdown. Cold review passed7,006 files/315
directories, five clean hives, exact tools and protected OS/seed. Only the
explicitly allowed CSS0.DAT and Game.cfg retail asset changes occurred. All owned
host processes are closed; no runtime may be reopened, recollected or parented.
No physical Xbox access occurred. The console remains last-known dashboard/no
owned hook;596 SOFTWARE cleanup remains cold-only. Packages,720p and the paused
automation are unchanged. See final001.json and staged review for closure pins.
