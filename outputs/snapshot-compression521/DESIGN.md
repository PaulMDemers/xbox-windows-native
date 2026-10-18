# Closed snapshot storage521

The existing768MiB projected emulator preparation reserve fails above the20GiB
free-space floor. This operation may losslessly compress only56 exact host-side
snapshot files: five hives and two event logs, before/after, from closed physical
501/508/514/518. These are retained readback copies on C, not console files,
installed files, executables, recovery256 or QCOW/VHD/backing-chain components.
No files are deleted, moved, replaced or semantically edited; paths and bytes
must remain identical to their historical recorded lengths/SHA256.

A separate read-only plan joins each file to completed stage/collection/final
records and validates the closed process state. It checks the exact canonical
allowlist, containment, every parent for reparse points, single-link regular-file
identity, no encryption/sparse/existing compression, NTFS compression support,
and actual allocated/logical bytes. The native compact.exe hash is pinned.

Application revalidates every precondition and original byte hash immediately
before one bounded native compression invocation with an explicit file list.
It never uses recursive selection or another drive. If capacity already meets
the existing guard, skip compression. Preserve tool output and failures; always
read back each selected file after an attempted invocation. Only unchanged byte
hashes/lengths/paths and observed allocated/free bytes support recovery claims.
No rerun of consumed compression attempts or automatic rollback/decompression.

An independent final review rehashes historical records, selected snapshots and
all new evidence, checks actual allocation/compression attributes and process
closure. The20GiB floor and768MiB projection stay unchanged. WSL backing capacity
shares C and is included. A later guest preflight must recheck actual free space.
No emulator, build, console, startup hook or new candidate execution occurs here.
