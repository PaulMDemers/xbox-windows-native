# Physical marker stopped on host-busy status

One exact468 build001 launch was accepted at01:28:03UTC on2026-10-18; dashboard
FTP returned01:28:26UTC. Complete primary preparation and192-byte refusal records
were read twice. Original launcher,startup,five hives,two event logs and video
trace are byte-identical. Five hives pass selected integrity checks; zero new
Windows events. No console C access, full FATX scan, Windows shutdown or new
human screen observation is claimed. Latest full physical E scan463 stays separate.

Actual first marker: result5; transaction0; started mask1; completed0; idle0;
first completion status0x0808;2 total status polls;4 I/O writes;0 acknowledgments;
3 timestamp reads. Start1967119314916, end1967119317860 ticks. The wrapper deliberately
refused before the original loader. The second marker was not reached. The raw
record does not reveal whether the hardware transaction completed later.

Pinned primary Linux nForce driver definitions identify0x0008 as host-busy and
0x0800 as bus-busy; the driver waits for these states. Our marker accepted only
the latter and therefore rejected a defined busy state. This is a diagnostic
bug, not evidence of an electrical failure or the historical boot issue.
See status-source-review.json for commit-pinned URLs/hashes and private source
snapshots. Upstream xemu performs this transaction synchronously, explaining a
model coverage gap; exact historical emulator source-to-binary identity was not
requalified by this source review.

The working path remains E:\Applications\XWNEBoot\default.xbe. Diagnostic folder
E:\Applications\XWNBoot468a is consumed; never launch it again. Private captures
are C:/xwn469/physical001. No further physical test is queued. Next correction
must wait on both busy bits within the same bounds, still refuse actual errors,
and preserve the full capture; marker-busy470 is host-only preparation for that.
