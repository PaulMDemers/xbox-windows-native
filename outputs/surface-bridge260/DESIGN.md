#260 — live reference inventory and sequenced renderer diagnostic

This is an opt-in emulator diagnostic. It grants no native GPU ownership and
changes no physical driver. It uses the unchanged reboot-held258 driver and259
probe. Legacy246 UI close/reopen remains one-shot;247 and227 must remain unused.

## Ownership and synchronization

Each accepted stage uses a fresh slot from a four-slot, process-lifetime array.
The monitor only queues work. The actual PFIFO worker halts the producer, waits
for a CPU-exclusive inventory acknowledgement, fences the render/display GL
contexts without holding BQL/FIFO/PG/renderer locks, and takes renderer/PG locks
with try-lock refusal. Queue emptiness on another thread is not an acknowledgement:
cpu-common.c removes work from its queue before executing it.

The CPU audit walks the actual callback list in exclusive context and rejects
unknown callback function, opaque owner or memory region. It runs after earlier
insert/remove jobs and rejects later queued work. Before and after snapshots must
contain the same unrelated callback tuples, with only the expected test callback
inserted, retained or removed. Existing244 events separately record allocation,
actual insertion, requested removal, unlink and free. A missing callback alone
does not establish that every required lifecycle event was captured.

The collector covers surfaces and current surface bindings, cached/bound textures,
palettes, vertex cache ranges and current enabled attributes, conservative scanout
and overlay tails, and actual CPU callbacks. An enabled vertex attribute with no
proven range is UNKNOWN and refuses admission. Pending primitive/report/download/
flush/context work refuses admission. Only the exact owned test surface/callback
is excluded at stage3 and is attested separately. Other surfaces must be younger
than the age-eviction threshold. Global frame time and other surface ages are never
changed.

The unchanged259 renderer routine has one actual260 worker caller now. It creates
a private-FBO age case, a dirty surface for a real guest CPU read, updates that
same texture before a real guest CPU store, and finally verifies that CPU data
survives retirement. It restores/rechecks GL state. The worker is no longer parked
when guest read/store callbacks need it. An uncertain or failed stage keeps the
producer halted and requires closing the sacrificial process, retaining evidence.
No failed slot is recycled and no published arena is freed/unloaded.

## Runtime attestation

Each of five native checkpoints must match its actual process, preferred image
base, resident probe instructions and exact callsite/stack arguments. The actual
loaded driver, relocated resident text and static Arena are checked. NT5 handle
table traversal must resolve the probe's current GENERIC_WRITE handle to that
Arena's FileObject, which must resolve back to the same driver. The probe does
not request FILE_READ_DATA; returning a buffered IOCTL payload does not require it.
The original overly restrictive attestor and decoder checks are preserved under
prior-attestation001; corrected complete-layout checks are in review002.

CR3 must match the owning process. Four independent page-table walks must resolve
the live arena virtual address to its actual contiguous physical pages. Only page
table words are physically read, with a forbidden-arena check and restoration of
GDB physical mode. The debugger never reads the dirty arena before the intended
guest access, writes guest registers/data, or supplies the expected readback.

One launch, bounded checkpoint waits, explicit breakpoint removal, final resume
only after full success, then one cold allocation/hive/protected-file/event audit.
The strict inherited Ft49 failure is retained. Full preservation additionally
requires independent lifecycle-event analysis; host comparisons are not callback
coverage. Neither a diagnostic pass nor historical fixture250/258 is qualification
of the audio-integrated physical demo.

## Preserved prelaunch failures

emu001 was refused by the projected20GiB C reserve before runner-start or xemu.
No guest collection applies. emu002 uses a new run identity and fresh run disk
copy of the same immutable, never-executed preparation. The first002 manifest
writer used a nonexistent parent filename after completing review; its source
and result are retained. complete-freeze002.py finishes only that missing manifest.
No source or gate was relaxed to recover either host failure.
