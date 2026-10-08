# Same-mode disable/re-enable: strict diagnostic PASS

Probe124 and unchanged RAM0109 passed a real Windows2000 same-mode reset at
1024x576x32,60Hz. The ordinary video-mode-reset run is separately qualified.
This fresh diagnostic captured both actual DrvAssertMode calls: FALSE then TRUE,
each returning1 on the same PDEV and primary surface. Live ShadowActive changed
1→0→1. Thread, stack cleanup, actual COFF-resolved entry PCs, relocated resident
code, return sites and stop chronology were independently checked. No surface or
PDEV replacement callbacks occurred; those paths remain unqualified by this test.

All104 raw physical framebuffer captures match:78 color-cursor states and26
restored backgrounds,10,223,616 RGB comparisons with zero mismatches. The oracle
uses26 exact persisted393216-byte references and each actual runtime marker's
digest. It does not claim live virtual reference residency. All26 reference SHA256s
also match the ordinary run and both incomplete diagnostic children. Ten mutations
cover wrong shape/hotspot, hidden/visible confusion and single RGB-bit corruption
before and after reset. Seven actual callback-record mutations are rejected.

371 resident pins include the complete11668-byte relocated display text. Display
PE header remains explicitly unreadable by GDB; loader identity, complete code
and cold file identity are required.121 real single-step requests include three
no-progress replies. Each was followed by a bounded additional step that advanced
the entry instruction, without rearming early, deduplicating markers or changing
guest registers/code. The underlying debugger/emulator cause remains unresolved.
All breakpoints removed and guest resumed; all owned processes are closed.

Guest completed26 GDI cases,78 cursor phases and2,555,904 exact readback pixels.
Normal shutdown1/dashboard. Full allocation325directories/6785files/326directory
clusters, zero errors/orphans; five structural hives and protected/payload/startup
hashes pass. Pagefile96MiB/1536clusters and inherited settings unchanged. Zero new
warning/error/application events. Shared framebuffer mapping/cache contract is
unchanged. No physical access, driver patch, device-policy change or speed claim.

The first two diagnostics remain strict failures: video-mode-trace captured five
matching frames before a repeated marker after a non-advancing step; trace2
captured three matching frames before a truncated live virtual reference dump.
Each closed cleanly and passed cold guest checks, without retroactive runtime PASS.
The first host pair-review incorrectly required unique fixture hashes; identical
inputs can produce byte-identical fixtures. Its failure and script are preserved.
history-review.py instead verifies four distinct fixture/private-run paths,
immutable backing parents, exact inputs and outcomes; it passes.

Read verification.json, transition-verification.json, step-verification.json,
oracle-tests.json and history-review.json. Candidate001 CLOSED: never relaunch or
recollect. New resolutions, surface replacement, boot-video/crash handoff and
physical qualification remain separate work.

The raw monitor-reply journal is13,081,610 bytes. It is preserved byte-for-byte in
candidate001/trace-parts with a SHA256 manifest, under the unchanged5MiB tracked
file limit. `archive-trace.py --restore` reconstructs/verifies the original local
candidate001/trace.json required by the verifiers. The local original is unchanged.
