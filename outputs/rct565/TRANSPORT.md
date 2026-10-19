# FTP transfer investigation

The user reported1,647MB free on console E. Recorded conservatively as decimal
bytes, that exceeds the533101681byte package plus128MiB spare. No cleanup of old
builds was needed for capacity.

Stage001 used a continuous64KiB-block upload. It verified the owner marker,
installation guide and809908byte game executable, but transfer was too slow to
finish the package within its bound. The owned process was stopped before the
startup hook. The partial PDF and all journal evidence were retained.

Small owned-file tests compared transport behavior:

| Probe | Upload | Result |
|---|---|---|
| 1 | Existing32KiB STOR/APPE chunks,1KiB blocks;512KiB | Exact readback,2.95seconds including readback |
| 2 | Continuous1KiB blocks;512KiB | Ten-second bound exceeded |
| 3 | Continuous1KiB blocks,1ms pause perblock;512KiB | Upload0.86seconds, exact readback |
| 4 | Continuous4KiB blocks,1ms pause;4MiB | Ten-second bound exceeded |
| 5 | Continuous1KiB blocks,1ms pause;4MiB | Upload6.49seconds, exact readback |

These measurements justify pacing this deployment; they do not identify a
particular TCP, adapter, dashboard or storage defect. They are not a general
FTP performance benchmark. Game/runner bytes were unchanged.

The immediate cleanup checks after timed-out probes2/4 incorrectly interpreted
an unavailable RETR as absence. Stage002's strict root-directory check refused
the subsequently visible partial files before writing anything. This failure
is preserved. A separate cleanup fetched and verified their known pattern
prefixes, deleted only those owned probe files, and confirmed absence through
two LIST checks three seconds apart. No probe file is part of the game package.

Stage003 used a new recovery journal. It revalidated unchanged baseline files,
the exact owner marker, the three completed files and the interrupted PDF's
expected prefix. It permits only the recorded directory/file set. Remaining
files used the paced transport and complete readback. It verified448files,
238.6MiB, before CSG8.DAT exceeded the180second per-file upload bound. The short
probe success did not generalize to the complete payload. No hook was installed.
The original failed stages and frozen controllers remain unchanged.

Stage004 preserves those verified files and checks the interrupted file prefix
before resuming. It uses the established32KiB STOR/APPE transactions, with1KiB
send blocks and full readback. It journals per-MiB upload progress, permits
600seconds per file and has a3600second supervisor bound. The hook remains last.

Use controller004/supervise004 for launch and collection, audit004 and
registry_review004 for final review. Their source and prior failure records
are pinned by transport-package003. Controller-host006's eleven transport-model
fault cases pass; only actual stage/launch/collection records establish console
outcomes. All transport revisions use the same original game/runner package.
