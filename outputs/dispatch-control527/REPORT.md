# 527: standard nxdk runtime control; physical receipts absent

The physical dashboard accepted one launch at 12:29:50.070241UTC. Neither
begin.bin nor entry.bin was present in the paired collection ending
12:32:16.682535UTC. This control supplies no physical entry, file-operation,
Windows, normal-restart or stability qualification. Missing receipts do not
prove no entry: the checked E-alias path or a file operation could also refuse.
The result makes a Windows-only explanation insufficient, without identifying
dashboard dispatch, the loader, nxdk initialization, aliasing or I/O as the cause.

The exact 102400-byte candidate has SHA256
fcc5536db1c27e5e3795151d9220cac9ce0487575b14a7b1c3cd33a66a0ccfbd.
It uses the standard nxdk runtime and two private application source files;
it is not another custom Xromwell entry patch. Shared SDK commit
58427c078b4ccb0121f359b6b6c536b3b2914976 remained unchanged. The leased dry run
compiled only main.c and engine.c. The sole warning was the previously observed
linker .edata/.rdata merge warning. No new compiler warning or shared SDK rebuild.

The actual portable engine passed 19 scenarios under ASan/UBSan with modeled OS
services. Independent decoding rejected112 transport/semantic mutations.
Thirty actual controller paths passed using modeled FTP/baseline/clock and an
explicitly modeled receipt; three real stand-in subprocesses covered normal
exit, failure, bounded timeout and duplicate refusal. These are host tests.

Fresh emulator002 ran the exact candidate on an unused blank8GiB-derived seed,
produced two actual48-byte receipts, observed kernel1.0.4627.1, and exited0
naturally without timeout/fallback. The second receipt proves the first's
write/flush/close/readback sequence completed; neither receipt proves its own
final close or the later firmware-return call. Cold E audit found5directories,
4files,15ownedclusters, zero errors/orphans. Only the two expected files were
added; both staged files were exact. Source seed/base/firmware inputs and private
EEPROM were unchanged. Complete virtual-map comparison found1034changedbytes,
including offset1540 outside E: strict disk isolation remains FALSE, with no
writer attribution or gate waiver. This is scoped runtime evidence only.

The physical attempt used /E/Applications/XWNDispatch527 and no Windows startup
hook. Stage/readback and paired post-run checks preserve the ordinary launcher,
normal startup and720p baseline. Console C was not accessed by this controller.
The final cold review records the five paired hives, two event logs and exact
before/staged bytes; dashboard reachability is not normal Windows restart.
No physical allocation or whole-disk equality claim is made.

Preserved failures: Run001 refused before launch because a PowerShell DateTime
UTC literal was converted to local time. Run002 corrected the comparison but
emulator001 exited1 before guest execution because its QCOW backing name used
a Linux absolute path. Its cold audit found no receipts. Fresh preparation002
uses a relative backing path, checked through Linux and Windows before Run003.
The cold reader also normalizes the FATX inventory path's lowercase spelling.
No closed runtime was reused or recollected. The new closed emulator001 private
executable alone was losslessly compressed, bytes rehashed, then hardlinked into
the separate emulator002 portable directory; no disk/backing image was moved.

The user has been asked whether they can watch a short visible launch control.
No further physical launch is queued. A visible marker independent of file I/O
is the next useful observation; another identical silent retry is not justified.
486 alpha arithmetic and496 combined-scene physical results remain pending.
