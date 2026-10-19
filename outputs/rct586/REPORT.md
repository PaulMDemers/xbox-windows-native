# PC586: corrected save-test preparation, no runtime admitted

The asset table is regenerated from pinned retail bytes, without attempt-number
substitution. An independent parser checks all502 names, sizes and SHA1 digests
against the SHA256-qualified source manifest. Negative tests reject altered
sizes, filenames, digests and duplicate names. The build reruns this check.

The frozen NT5 build passed its PE/import/source checks. Independent media
readback verified all502 reconstructed files. These are host preparation
results only: the Save dialog helper has not yet been exercised successfully.

Fresh fixture preparation stopped before disk creation because free space was
21,800,988,672 bytes, below the22,548,578,304-byte admission threshold (21GiB).
The20GiB reserve remains intact. No guest or console launch occurred, no save
exists, and no closed runtime was reused. The failed admission is preserved in
[preparation001-failure.json](preparation001-failure.json). The enclosing lease
wrapper returned0 despite the Python exception; the missing fixture/receipt and
exception establish failure, not the wrapper's exit code.

The read-only [API inventory](api-inventory001.json) finds imports for
GetProcAddress and LoadLibraryA but no static DirectDrawCreate import in the
pinned Deluxe executable. Earlier PC568 runtime evidence included DDRAW.DLL.
This makes dynamic API resolution a useful future observation point. Static
imports/literals and module loading do not establish calls, surface types,
acceleration, timings or FPS. No executable modification or trace was run.

Next: recover enough verified capacity, then admit a fresh immutable404 child
and validate Save followed by normal restart and cold save readback. Only then
admit the planned second boot and prove Load restores the saved scene after a
deliberate camera change. Maintain separate PC and Xbox qualifications.

## Capacity recovery and its limits

Lossless NTFS compression was requested for2,005 tracked public text records.
Every file's SHA256 remained unchanged. Free space increased by80,326,656 bytes
during that operation; concurrent host activity can affect that difference.
This did not restore the21GiB admission threshold.

A proposed lossless archive of closed585's disposable disk stopped during its
dependency check: Python's WSL traversal exceeded90seconds. A separate native
inventory also reached its45-second bound (exit124). Both failures are retained.
No disk was compressed into an archive, removed, reopened or reparented. The
original585 disk hash was rechecked and still matches its closed record. No
owned emulator or inventory process remained after cleanup.

These are capacity/preflight failures, not game results. Further archival must
first establish a complete dependency inventory with a new bounded procedure;
do not bypass that check or retry these attempts as though they had not run.
