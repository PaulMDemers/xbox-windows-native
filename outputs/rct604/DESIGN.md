# PC604: bounded bitmap header observation

Keep the original601 graphics, recursive call and output checks intact. Extend
only this new control and observer. No game, functional driver or physical access.
Read at most4 bytes followed by40 bytes through checked ReadProcessMemory, and
record raw words, address, status and derived extent for each selected header.
Interpret only the40-byte BI_RGB header, dimensions bounded to16384 and pixel
extent to64MiB. Other layouts are explicitly unsupported; no palette/mask/pixel
payload is read or inferred. Zero biSizeImage is permitted for this RGB layout.

At real CreateDIBSection and StretchDIBits entry, snapshot their actual argument.
An exported original probe exercises two signed-height cases plus null, address
wrap, inaccessible page, truncated page-boundary header, unsupported size,
invalid dimensions/planes/bpp/compression, extent budget, sizeimage and palette
count. These invalid pointers go only to the no-dereference original probe,
never to GDI. A guarded allocation supplies actual inaccessible memory on NT5.

Run pristine and observed subjects once in a new immutable404 child. Compare
their independent graphics result logs, retained arithmetic and actual observer
records. Use a separate Python decoder and adversarial trace mutations, and
the shared C reader with host callbacks that enforce read sizes/counts, including
partial-read corruption and header changes. Require normal restart and cold
readback with exact binaries, five hive checks and correct EventLog6006 delta.
Every failed build/review stays recorded. No scene costs, FPS or GPU claims.
