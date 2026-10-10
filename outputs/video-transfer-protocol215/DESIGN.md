# Bounded transfer protocol215

This kit contains an authored CPU command planner and a serialized lifetime
model. There is no NT5 runtime adapter or GPU-writing path. It specifies a first
disjoint copy up to16x8 pixels, using source, destination, completion and command
pages with independent bounds. Synthetic test addresses are not proposed native
allocations. The actual fixture fails submission preflight for missing contracts.

The intended allocation precursor is213's16KiB resident UC buffer, split into
four4KiB pages only after actual per-page translations and lifetime are checked.
No physical address from213 or the host oracle may be reused by assumption.
Each DMA descriptor covers only its own page/range. GPU address/target/class,
CPU/GPU visibility and resident ownership must be verified by a new native
adapter. Neither EngLockSurface nor ShadowBits translation establishes this.

The exact compiled xemu source was reconstructed into private copies from pinned
originals plus the already-built resource and CPU-surface patches. All13 copied
files match the685f24e3 candidate manifest. No borrowed source changed. Inventory
findings narrow the protocol:

- USER supports DMA for the current channel; PIO and another channel assert.
- Class39 is defined but has no PGRAPH method case. Classes62 and9f implement
  surfaces2D and blit. Both rendering paths copy rows in host memory; their
  success or timing cannot establish hardware speed.
- RAMHT lookup uses one hashed slot. It neither implements collision search nor
  establishes correct object identity from valid/channel/engine alone. The
  planner emits seven unique, bounded slots and does not overwrite an existing
  table. The host oracle assumes an isolated granted table; the real grant is
  absent. Observed214 RAMHT03000100 decodes to base10000,size1000,searchfield3.
- DMA mapping masks address to27 bits, ignores target/class validation and
  returns the limit without adding1. Full rectangle spans are not checked there.
  The planner uses64-bit arithmetic, rejects truncated/overlapping ranges and
  stays below the retained framebuffer reservation. These restrictions cannot
  prove physical descriptor semantics.
- A8R8G8B8 preserves all four bytes in the selected blit path. Other XRGB formats
  can rewrite alpha. The first exact byte test therefore selects format0a and
  SRCCOPY3 with zero input/output points.
- Kelvin97 is restricted to subchannel0. Its backend semaphore method calls
  surface_update before the32-bit store. This is a source ordering observation;
  the actual hardware completion/CPU visibility contract remains unverified.
- A channel/context mismatch stalls for software context-switch interrupt
  handling. The model asserts on hardware context switching. The existing NT5
  miniport has no corresponding context handler.

The proposed27-word/108-byte increasing-method packet binds97 on subchannel0,
sets its completion DMA handle and offset16, binds62 on subchannel1, assigns
source/destination DMA handles and format/pitches/offsets, then binds9f on
subchannel2 and assigns surfaces/operation/points/size. The final command is
97 backend semaphore release with the nonzero context generation as its token.
There are no jumps, ring wrap, scanout writes, resets, acknowledgement writes or
unbounded waits. Numeric definitions and contiguous method fields are checked
against the actual compiled header, not an assumed compatible graphics class.

Pure planner results do not confer ownership. The example RAMHT12000,objects18000
and pages200000 onward are synthetic host addresses only. The retained Control
mapping681000 excludes both PRAMIN700000 and USER800000. Register stability,
GET==PUT or a valid-looking table entry cannot establish exclusive control.

The lifetime model requires external serialization and six real witnesses:
resident allocation, instance-memory ownership, quiescent context ownership,
validated DMA addressing, completion ordering/visibility and a cleared token.
Tests supply mock witnesses. A native caller must gather evidence for each one;
setting bits cannot substitute for it. Future global generations must be unique,
nonzero and refuse32-bit wrap. Caller storage/packets remain immutable while
exposed. No such manager or caller exists in215.

Preparation verifies the final packet length/header/token matches its generation.
EXPOSED must be recorded before the first GPU-visible instance/configuration
write. Any partial initialization or uncertain doorbell can then quarantine the
entire allocation. Submission begins bounded observation. Foreign-generation
callbacks are rejected; a stale nonzero token, fault, clock regression or deadline
causes terminal quarantine. A late matching token cannot make quarantine freeable.
Completion is separate from drain. Drain requires current-generation evidence
that the producer stopped, references ended and ownership was restored. Release
is allowed only before exposure or after that drain. No assumed reset or register
equality serves as the drain witness.

Quarantine deliberately has no reset/recovery/release transition in this first
model. A future native driver must retain the allocation across timeouts and
crash/display handoff until a separately verified recovery can revoke references.
The existing reset callback returningTRUE is not that proof. Ordinary display
CPU paths and shared framebuffer ownership must remain usable without depending
on completion of this diagnostic context.

No Windows/xemu run, physical access, allocator call, MMIO operation, cache/mode
change, IRQ suppression or event waiver occurred in215. Strict214 Ftdisk49 remains
recorded. The physical0101/video0093 baseline,0088 rollback and0.1.0 are unchanged.
