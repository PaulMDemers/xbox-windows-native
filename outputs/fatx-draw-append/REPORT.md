# Paced append control and simultaneous GDI load both passed

7 October2026 UTC. The two fresh sibling fixtures used the same settled parent,
reviewed helper, startup, FATX0101 and video0093. The only staged payload byte
change was drawmode.txt:0 for control,1 for drawing. All16 corresponding cold
file hashes match each other and the independent expected-byte oracle.

| Case | Draw mode | Launch UTC | Dashboard return UTC | Workload ms | Completed drawing cycles | Result |
|---|---:|---|---|---:|---:|---|
| 001 | 0 | 04:00:22 | 04:02:15 | 29400 | 0 | PASS |
| 002 | 1 | 04:04:36 | 04:06:47 | 51975 | 1644 | PASS |

Together:16,384 successful appends,32 exact files,15,977,216 exact cold payload
bytes. Same four initial offsets401/3985/65425/270225, two explicit flush policies,
two handle lifetimes,512 appends/file with sizes219/110/111/112/221/4097 cycling.
Both sleep1ms each16 operations. Source checksums/post-call bytes, completion
counts, explicit flush/close, live readback and cold oracle checks passed.

Drawing used an owned window, compatible512x320 bitmap, eight solid-color bands,
BitBlt and GdiFlush. It completed1644 cycles,1583 of which began and completed
within a single numbered append epoch. Every case had positive overlap:
444,270,98,100,100,115,102,100,32,31,31,31,32,35,31,31.
Control had zero loop drawing cycles. Startup/join and GDI cleanup passed, with
zero recorded GDI errors and zero thread exit error. Epoch checks avoid counting
one operation that spans the inactive gap between different test cases.

Each run has one normal shutdown, no new unexpected warning/error, popup or
application event, five fully walked hives, unchanged protected/runtime/boot
hashes, exact output directory17files, unchanged SetupAPI log, and full F
allocation consistency. Before:322dirs6752files323dirclusters. After:
323dirs6769files324dirclusters. Zero orphan clusters or allocation errors.
Identical historical SCM/Ftdisk records retain their explicit classification.

This demonstrates known-source append persistence under this bounded GDI API
load in xemu. It does not benchmark the video driver, verify displayed pixels,
exercise GPU acceleration, reproduce actual SetupAPI source-buffer behavior, or
exclude intermittent physical corruption. Workload times are observations only.
The parent retains its documented emulator-specific historical device policy.
No debugger, host recorder, window automation, raw runtime disk access or driver
change was used. No physical Xbox contact, reset, deployment or new recovery
snapshot; original0088, immutable0.1.0 and all historical failures remain intact.

Both owned runners/supervisors and cold readers closed. All completed stages are
immutable; do not rerun them. comparison.json pins the pair's qualification hashes;
qualifications pin audit/allocation/collection/launch/preflight evidence. The
reviewed PE imports were checked against owned Windows2000 DLL exports and the
pinned compiler/source/build hashes are in probe-review.json. Raw disks and media
stay private and ignored. NEXT.md specifies the separately coordinated aligned
first-install plus drawing experiment; the hardware anomaly is still unresolved.
