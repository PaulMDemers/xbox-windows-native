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
