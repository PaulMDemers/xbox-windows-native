#654: one sustained timing-readback comparison; physical observation pending

This diagnostic answers one question: does the captured post-result timing
subset match the requested480p profile? It replaces651's four-slot failure
sequence with one20-second indication on both supported success and vblank
failure outcomes. It is not a timing fix, complete snapshot export, or evidence
of Windows boot. No physical launch/result exists yet; read actual stage/launch
records and NEXT.md before continuing.

Preparation and staging have completed:28 selected baseline files read twice;
owner marker and XBE read back exactly at E:/Applications/XWNFocus654.
No SITE, hook, rollback or observer exists. Dashboard was reachable during
staging. Fresh watched readiness requested; no automatic launch is queued.

## Transport decision

The pinned651 source review passes10 checks (`source-review001.json`). Display
setup precedes STI, USB and IDE initialization. Failure capture is followed by
the existing reset/halt path, which cannot reach a later disk export. Success
returns through further framebuffer/interrupt-control writes, then normal boot
initialization; a later snapshot would not be the same phase as the saved one.

BootPciInterruptEnable executes STI. The653 PIO backend rejects IF set, so it
cannot simply be attached after BootIdeInit. BootIdeInit also changes bus-master
state and initializes both drives; moving it earlier would change the display
experiment. The inspected FATX facade exposes reads/file loading, not a file-write
API. Existing serial output has an unbounded wait and no established receiver.
The loader later disables interrupts, changes CPU/memory state and moves its
image, with no explicit651 snapshot handoff in that code. RAM survival is unknown.

Decision: defer native storage integration and use the existing post-result LED
output for a smaller, interpretable question. No IDE ordering, interrupt state,
pending-bit policy, display predicate, poll limit or reset cleanup was changed.
The earlier request for complete automatic pre/post receipts remains unmet.
652/653 models remain valid host evidence, not a deployed logger.

## What to watch

After a two-second dark delimiter, one pattern is held for20 requested seconds.
Ignore ordinary boot LEDs after that interval. The existing timer supplies the
delay; the duration is not a verified physical wall-clock bound.

| Pattern during the sustained interval | Meaning |
| --- | --- |
| Green/off |Compared CRTC and FP/general timing subset matches|
| Red/off |CRTC subset mismatch only|
| Amber/off |FP/general subset mismatch only|
| Red/amber |Both subsets mismatch|
| Red/green |Unknown/incomplete capture or an outcome outside this comparison|

Green here **does not mean Windows boot success**. Record the screen outcome
separately. Missing or partial indication is inconclusive. Red/green does not
identify a vblank timeout in this654 test. The match mask does not compare the
captured VPLL, PCRTC configuration or handshake; it cannot establish effective
clock, routing, a specific bad register, or all hardware state.

The source accepts comparison only for result1/stage5/error0 or result-1/
stage255/error22, with a captured post-result snapshot and match mask0..3.
Other outcomes are unknown. Failed-wait phase/status/handshake no longer have
individual LED slots; their detailed records remain RAM-only.

## Change and validation

The fresh source export differs from pinned651 tree
`2fda813f3b8109dfc6b70f6d37e21d2cf9a66d55` only in `drivers/video/led651.h`.
The old filename/ABI is retained deliberately so the native capture/apply/reset
source is byte-identical. Selection/index restoration and post-failure-blanking
capture are unchanged. This still changes code layout and time spent indicating
after setup; it is not a repeatability control or a functional repair.

- 9,600 new ASan/UBSan host cases cover result/stage/error/capture/comparison
 combinations and failure at each of the four LED writes, with no retry.
- 100 new exact linked-wrapper cases exercise capture, indexed-register restore,
 comparison, LED ordering/delays, write failures, success return and original
 reset/halt behavior using modeled setup/hardware callbacks.
- 8 compiled sections match651: .text/.rodata of adapter, profile, BootLibrary
 and BootInterrupts. Timer and display protocol are unchanged, not requalified
 by a physical run. All source and binary pins are retained in build/review JSON.
- Accepted/uncertain launch controller tests pass: one request,20-second reply
 bound, no duplicate. Host tests made no console connection.

Private XBE: `C:/xwn654/build001/default.xbe`,303120 bytes,
SHA256 `0457913a58cb6030c1b54a0078da2b96e8939f4070412c783aa4219241ab2bb1`.
New sources/build/temp files are on C;20.05GiB build reserve and WSL backing
volume checked. All build/test processes exited and the build lease released.
No VM, disk image, historical deletion or recovery copy was made.

No654 build/test failure occurred. An exploratory rg search using wildcard path
arguments failed with OS error123; the corrected directory search and source
review completed. Prior failures and closed runtimes remain untouched.

## Physical workflow

Preparation and staging use only the unique E:/Applications/XWNFocus654 path
and private C:/xwn654/physical001 evidence. No startup hook or dashboard C access.
Ordinary720p/startup and saved XBOX480 are checked against protected identities;
preparation retains28 selected files with repeated readback. The new executable
and owner marker must read back exactly before a launch is admitted.

A watched-readiness response is required for interpreting the sustained interval,
not additional routine launch permission. If Windows opens, leave it running
until normal Restart is requested. The bounded observer collects once on actual
dashboard return; retained records then receive selected-file/hive/event checks.
FTP return alone is not normal shutdown. Ftdisk49/Popup26 limits remain.

651 and earlier attempts stay closed. No new hardware or mode qualification is
claimed. Automation stays paused and the original physical lease is retained.
