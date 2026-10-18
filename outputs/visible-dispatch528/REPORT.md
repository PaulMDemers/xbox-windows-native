# 528 visible control prepared; physical observation pending

The 110592-byte candidate SHA256 is
d2f32d69247358bddb7dad4274789c8645e496bfe60476ccd41889a39fc24499.
The new standalone nxdk candidate is built and has a scoped actual emulator
receipt pass. It has NOT been staged or launched on the physical Xbox. The
screen-observer availability question remains unanswered; no launch is queued.
The next physical observation is intended to distinguish an early visible
runtime marker from later E-alias or file-I/O failure. It is not a Windows fix.

The application requests standard720p, verifies returned mode/framebuffer and
actual MmQueryAllocationSize before bounded pixel writes, shows a blue band
before E-alias/file operations, waits12seconds, displays each API outcome and a
green/red result band, then waits20seconds before requesting firmware return.
The standard SDK's XVideoVideoMemorySize is a hardcoded4MiB value, so it was not
used as allocation evidence. The SDK's video initialization itself programs the
display; this is a temporary standalone mode, not a Windows configuration edit.
nxdk CRT/automaticDmount precede main and cannot be distinguished by absence of
the early marker. Existing E aliases still require the exact standard target;
no alias replacement or speculative normalization was introduced.

Host evidence: actual C engine19 scenarios and112 independent transport rejects;
actual application main/UI30 scenarios under ASan/UBSan with modeled SDK APIs;
actual controller30 modeled-FTP cases; three real supervised child lifetimes;
five actual socket-transport cases with a modeled HMP server. The UI tests cover
mode/allocation failures, early-marker ordering, alias statuses and control
characters, all14 file-operation failures, short/extra reads and byte mismatch.
These models do not prove physical GPU, alias, loader or file-service behavior.

The leased private build compiled only main.c/engine.c against pinned nxdk
58427c078b4ccb0121f359b6b6c536b3b2914976. All1661 SDK pins (including the inspected
video/debug/mount/automount sources), tool pins and build outputs were exact.
Only the inherited .edata/.rdata linker warning occurred.

Emulator001 used the exact built ISO/candidate and fresh unused blank8GiB-derived
preparation002. It wrote actual begin/entry48-byte receipts, kernel1.0.4627.1,
and exited0 naturally at12:47:54.9433589UTC (PID30484), no timeout/fallback.
Cold E graph5directories4files15clusters, zero errors/orphans; only expected
receipts added and staged files unchanged. Source seed/base/firmware and private
EEPROM unchanged. Full-map comparison1034changedbytes includes offset1540
outside E: strict disk isolation FALSE; no writer attribution or gate waiver.
This qualifies earlier begin pipeline completion, not entry's own final close,
rendered output, normal Windows restart or physical stability.

The first screenshot requests produced no files and had no recorded replies.
An improved acknowledged transport was host-tested, then used on separate fresh
emulator002 with the same exact candidate and never-executed preparation parent.
The actual monitor replied "unknown command: 'screendump'". This identifies a
capture capability limitation, not an application failure. The runner stopped
the attempt with its recorded fallback kill at12:50:56.9718316UTC, PID27744,
exit-1. Cold audit found no receipts, complete virtual disk equality to the seed,
unchanged inputs/EEPROM and zero E allocation errors. Receipt absence is not
no-entry proof. No images were created; visible colors/text remain UNVERIFIED.
Do not rerun either closed runtime or claim a visual pass from modeled pixels.

Preparation001 was refused before any fixture/launch because the projected
768MiB reserve would cross the20GiB C guard. Thirty-eight newly closed528 host
fixture XBE copies were losslessly compressed and rehashed. That was insufficient;
one separately selected, proven-closed524 nonbacking executable was compressed
once, preserving bytes/path/file identity/single link and saving135217152 actual
allocated bytes. No prior523 compression case was repeated; no backing image or
historical file was deleted/moved. Guarded preparation002 then succeeded.

All owned processes are closed. The console was last observed at the dashboard
during527 collection12:32:16UTC;528 has made no physical connection or change.
Ordinary launcher/startup,720p baseline, Ft49/shutdown limitations and all earlier
failures remain.486 alpha arithmetic and496 combined-scene hardware tests remain
pending. No GPU/game/release or repeat-boot-stability promotion.
