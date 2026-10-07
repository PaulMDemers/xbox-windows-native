# Runtime mapping lifecycle of the actual installer

This diagnostic tests a statically identified candidate in the pinned original
SetupAPI DLL. It reuses a fresh child of the same immutable aligned installation
fixture and unchanged FATX0101/video0093. No physical access or guest data edits.

Case001 required instruction bytes and a live PE header but failed on an
unlocated unreadable-memory request before its first verified hit. Case002
verifies up to32 pinned resident code bytes per site and independently checks
the complete original DLL hash in both immutable and closed disks. Unreadable
code hits are retained as coverage gaps, never decoded as verified calls.
It filters by the actual wide filename ending in SetupAPI.log, records the
two source strings, mapping size/access, mapped append bytes before the seek,
then unmap, mapping-close, SetEndOfFile, file-close and outer return results.
Pairing uses thread plus outer/helper/cleanup frames. Other candidate paths and
unpaired sites are explicit. No candidate hit means no runtime coverage.

Reads are bounded and failure is preserved. The tested bounded atomic JSON
writer protects publication from transient Windows reader-sharing conflicts.
The tracer never asks the guest to page in a buffer, invokes a guest API, or
changes driver data/arguments. Only debugger breakpoints and steps affect timing.

The owned supervisor launches once through localhost4596 and waits for normal
dashboard return and tracer cleanup before closing the emulator. The ordinary
cold-audit suite still requires exact warning bytes, normal-shutdown evidence,
complete allocation, five structural hives, selected unchanged binaries and
installer completion. Passing those checks is a debugger diagnostic result,
never physical or ordinary stability qualification.

Use prepare.py and audit-before.py once per new case, then Run.ps1, trace.py and
supervise.py. After owned cleanup: trial.py collect, then analyze.py. Keep all
private raw buffers/disks/hives outside Git, with source/evidence hashes in the
reviewed report. This investigation follows the separate intentional-stop cases
in ../fatx-interrupted-append; none of their interruption gates are relaxed here.
