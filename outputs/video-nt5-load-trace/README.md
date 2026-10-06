# NT5 display image-load failure

Three owned emulator debugger runs reproduce the installed package boot failure.
The physical console, candidate0093 and release0.1.0 were not accessed or changed.
Each run uses the immutable `video-nt5-display-package-005` seed: completed INF
installation plus the previously documented offline Start=1 diagnostic. No guest
file, register or data-memory edits were made by the tracer. Execution breakpoints
and pauses make these exploratory runs, not ordinary timing or stability passes.

1. `001/trace.json`: the GPU device reaches IopCallDriverAddDevice. MmLoadSystemImage
   requests `xboxvnt5.sys` twice and returns `0xc000026c`, before DriverEntry.
2. `002/trace.json`: a verified breakpoint at the kernel's error conversion shows
   the underlying status is `0xc0000221`, image checksum mismatch.
3. `003/trace.json`: the checksum routine returns false for a 42,215-byte mapping.
   Both miniport captures match the on-disk file byte-for-byte within EOF, SHA256
   `e8021879bd606eb9cfc6927fbf50565c41781779af86e56f4678fa890b6eb6ec`.
   The first byte beyond EOF is `0x97`, followed by more sector slack.

The matching NT5 checksum implementation sums `(file_size+1)/2` words, so an
odd-length file includes the following byte. `checksum-replay.py` runs the owned
checksum instructions under Unicorn, stubbing only PE-header lookup. The original
captured tail returns false; changing only that extra byte to zero returns true.
The stored checksum and independently calculated PE checksum both equal 0x178e0.
This is not a corrupted miniport or an incorrect checksum field.

`trace.py` discovers the live kernel mapping and verifies entry bytes against the
owned kernel before arming breakpoints. It records entry/return stack pairing and
removes all breakpoints before signalling owned cleanup. Cases001-003 all ended
at 0xB4 and are closed. No hardware or ordinary boot qualification follows.

Interpretation limits: return EAX for void functions is not an NTSTATUS. The
`checking_image` field is only the most recent image-entry hint, not a thread-aware
association. In003, mapped-238.bin and mapped-475.bin are the exact miniport;
mapped-482.bin is a different 88,048-byte image and must not be attributed to it.

The fix and ordinary follow-ups are in [fatx-paging-eof](../fatx-paging-eof/README.md).
Allocation slack must not appear beyond logical EOF in a regular-file paging view.
That invariant is transferable to other FATX implementations; the NT-specific
checksum behavior and MDL mechanism are not Linux implementation requirements.

Private RAM and three older closed CPU logs were copied to an E: archive with
readback SHA256 verification before their C: copies were removed. Exact old/new
paths and hashes are in `evidence-archive.json`. QCOW files/backing chains were
not moved. The old crash decoder accepts `--ram` for these archived captures.
