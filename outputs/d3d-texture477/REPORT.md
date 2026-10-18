# 477 closed: malformed test floppy, no texture runtime result

The new texture sample compiled without warnings and passed three host oracle
tests, including 8,704 pixel/source mutations. It was not executed in this PC
attempt. The kit generator's unrestricted namespace replacement changed the
floppy size from 1,474,560 to 1,477,560 bytes. Windows booted normally but `DIR A:`
showed no files and the controller could not be found. No `C:\xwn477` output
namespace was created.

Preserve every input and UI journal. Explicit shorter key holds were added while
diagnosing command entry; that change did not fix the malformed floppy and is
not evidence that input timing caused the failure. The attempt ended through
the normal Windows Security → Restart UI, followed by QEMU exit 0 without a host
quit or deadline. Cold audit and immutable-input evidence are in final-review.

The sample executable remains unchanged. Fresh 479 uses a new child of the
reusable 404 source, token-bounded naming, and a strict FAT12 floppy decoder.
The decoder rejects this actual bad length and checks geometry, both FAT copies,
complete file chains/content, crosslinks and orphan allocation before launch.
No repair or relaunch of 477 is allowed. Physical478 remains unbuilt until a new
PC control passes. No driver, SDK or console changes occurred in 477.
