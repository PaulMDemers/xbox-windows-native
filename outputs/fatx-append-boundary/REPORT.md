# Append boundary results — 7 October 2026

Both ordinary emulator runs passed all 96 cases. Across the two fresh sibling
fixtures, 192 payloads matched the independent expected bytes after normal guest
restart and owned emulator cleanup. Neither run reproduced the physical setup
log corruption. The physical Xbox was not contacted or changed during this work.

| Evidence | Case 001 | Case 002 |
|---|---:|---:|
| Completed cases | 96 | 96 |
| Exact cold payload bytes | 8,238,784 | 8,238,784 |
| Helper elapsed time, milliseconds | 7,245 | 3,975 |
| Normal shutdown events | 1 | 1 |
| New unexpected errors / popups / application records | 0 / 0 / 0 | 0 / 0 / 0 |
| Parseable system hives | 5 | 5 |
| Allocation directories / files | 323 / 6,850 | 323 / 6,850 |
| Orphan clusters / allocation errors | 0 / 0 | 0 / 0 |

These elapsed times are incidental, not a performance comparison. Both runs
retained the identical historical HID service SCM7000 error; that explicit
emulator classification is recorded rather than described as an error-free
Windows configuration. SetupAPI's 144,784-byte log remained byte-identical in
both runs, so neither involved another GPU installation. Exact 0101/video0093,
loader, helper and reviewed runtime identities remained unchanged.

The helper checks seed/append source buffers, returned counts and live bytes;
the host separately recreates each expected file and checks cold bytes, event
deltas, hives and allocation. The matrix includes the original 270,225-byte
starting offset, as well as sector, page and FATX cluster boundary variants.
Every seed and final append is explicitly flushed. This is useful evidence for
these ordinary write paths; it does not establish the cause of the first-install
anomaly, exclude timing-sensitive corruption or test independent write-through
durability guarantees. There was no debugger or host-recorder intervention.

Source, build/import review, immutable fixture manifests, launch/collection
records and qualification reports are retained here. Raw disks, guest files and
built binaries remain private artifacts. The folder's Git attributes preserve
exact text bytes so recorded SHA256 evidence survives checkout; run
verify-evidence.py after staging to verify source and report identities.

Next: a separately identified repeated append workload with end-only versus
per-append flush, followed by a controlled first-GPU-install scenario with a
settled-boot control. See NEXT.md. Keep the original physical malformed log,
remaining hardware prompts and raw-C warning as unresolved evidence. No new
physical qualification, recovery snapshot or release tag was created.
