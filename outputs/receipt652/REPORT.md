#652: diagnostic receipt prototype; physical transport not qualified

651 reached the Windows desktop and recorded a normal restart, but its observed
LED sequence did not provide a complete register/status report.652 adds a small
binary report and a guarded, one-shot storage protocol. It has no Xbox backend,
no new XBE, no VM and no physical access.651 and all earlier attempts stay closed.

## Early-boot feasibility findings

The pinned651 source calls video setup at BootResetAction.c:95. Interrupt enable
and USB setup follow; BootIdeInit is not called until line211. The failure path
in xwn_hd_native.c requests reset and halts before returning to BootResetAction.
Logging only after ordinary IDE initialization would therefore miss these failures.

The older461 logger uses Xbox kernel file APIs before the privileged handoff.
The later Xromwell setup runs after xbeboot.S disables paging and replaces CR3.
Calling those old kernel thunks from this context has no established validity.
Restoring or borrowing firmware CPU/interrupt state is not proposed.

The existing BootIdeWriteSector is explicitly marked experimental and expects
initialized tsaHarddiskInfo. BootIdeWriteData calls BootIdeWaitDataReady but its
error return check is commented out, so it can enter its output loop even after
that wait fails. BootIdeIssueAtaCommand similarly ignores its first wait result.
These routines cannot serve as a fail-closed early logger unchanged. Their wait
loops also call existing timer delays; a loop count alone does not establish an
end-to-end bound. This is source inspection, not a newly observed disk failure.

Existing serial_putchar spins without a limit waiting for THRE. A bounded serial
backend would need a confirmed physical receiver; no receiver is established in
this session. A framebuffer-only report would not cover a blank failed mode.
RAM retention over reset and subsequent dashboard allocation is unqualified.

See source-review002.json for pinned source hashes and
the automated ordering checks. No functional display or storage patch was made.

## Implemented and tested

receipt.c encodes explicit little-endian fields into a1,536-byte slot containing
both snapshots, original aggregate wait observations, request/state, attempt ID
and candidate digest. A separate commit sector binds the complete payload with
CRC. The decoder independently uses Python struct and zlib. FORMAT.md specifies
every field, validity limit and callback precondition.

The storage engine refuses a nonmatching initial slot before writing. It writes
payload, flushes and reads back, then writes the commit, flushes and reads back
again. All operations are one-shot; any failure consumes the attempt. It cannot
allocate a file, select a physical LBA, clear a device interrupt or call firmware.

- Host ASan/UBSan validation passed17,025 checks. Cases include all12,288 single
  bit corruptions, every torn write prefix for all three writes, all1,536 seed
  byte corruptions, failures before/after every callback and refusal to retry.
- Independent Python oracle passed13,847 checks: exact C-produced bytes, every
  truncation, every single-bit corruption, foreign identities and semantic
  errors with recalculated checksums.
- The explicit field bridge passed1,401 ASan/UBSan cases using the actual651
  headers. It preserves all174 raw observation words, missing/partial capture
  flags and IF-set skip values. Its output matches the independent format oracle;
  its i386 object has no undefined symbols. No native hook is installed.
- The i386 freestanding protocol object has no undefined symbols. Execution of its exact
  linked code passed27 success/failure cases with modeled read/write/flush
  callbacks, ABI/IF preservation, ordering and retry refusal. This is CPU-level
  test execution, not a physical transport or boot test.

All artifacts are small C-volume files under C:/xwn652. The validation used the
existing build lease, pinned GCC12 and reserve checks including the WSL backing
volume. Leases were released and no owned process remains. Model output is
explicitly synthetic and private; no proprietary payload is published.

## What this establishes and what remains

The format and storage protocol are tested components. A valid CRC does not
establish the producer's capture point, successful flush acknowledgment, safe
physical addressing or device durability. The callback model deliberately
demonstrates that valid bytes may coexist with an uncertain operation result.

Next is a separately validated native transport and integration of the tested
snapshot-to-record bridge. The preferred design to evaluate is a preallocated file established
under the live Xbox kernel, with independently verified file extents and a
bounded native PIO backend used only after snapshots. This is a design direction,
not an approved physical writer: disk identity, controller readiness, DMA state,
allocation ownership, all timeout/error paths, flush behavior and exact caller
context must be established before staging it. No change to display polling or
clock programming follows from652.

The console remains in the last observed dashboard state. Ordinary720p/startup
are untouched, no hook exists, and no hardware observation is needed for652.

## Preserved review failure

source-review001.json failed after three successful source checks because its
section-end lookup expected different spacing in a comment. source_review.py
and that result are retained unchanged. source_review_v2.py uses the actual
next function signature; source-review002.json passes seven checks against the
same pinned source. This was a checker error, not a native build or hardware
failure. No validation outcome was overwritten.
