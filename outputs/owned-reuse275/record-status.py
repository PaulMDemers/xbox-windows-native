"""Record closed evidence and prepend continuation without rewriting history."""
import datetime,hashlib,json
from pathlib import Path
k=Path(__file__).resolve().parent
src=k.parent/'owner-boundary274/renderer-delta002.patch'
s=src.read_text();gate=s.index('if (s->accounting_error || s->shader_jobs_unknown || v->cpu[0].count)')
rows=s.index('if (!x265_add(&s->ledger,17,phase,')
assert gate<rows
r=dict(source=str(src),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
    zero_count_refusal_precedes_kind17_rows=True,full_existing_pages_cannot_reveal_failed_cpu_inventory=True,
    guest_relaunch_required_now=False,next='New read-only acquire-published terminal-refusal CPU inventory property; preserve original gate')
dest=k/'callback-source-review.json';assert not dest.exists();dest.write_text(json.dumps(r,indent=2)+'\n')
p=k.parent/'engineering-notes/CONTINUATION.md'
prefix='''#275 CLOSED — initial four-callback refusal, plus host recorder failure

Read outputs/owned-reuse275/REPORT.md, DESIGN.md, NEXT.md, final-review.json,
callback-source-review.json and actual records. All owned sessions CLOSED,
including runner55353. No release/native/SDK/physical changes. Never relaunch,
recollect or parent275emu001 or earlier closed cases.

Launch00:42:30UTC, closed00:42:47UTC. One phase11 actual XBE/text/kernel-export/
allocation attestation;720 independent framebuffer bytes,16384 source/guard
bytes,384 vertices exact. All15 RAMHT descriptors captured, exact DMA fields
and class/channel/hash/instance checks; graphics mutable bits not all decoded.
Retained owned pushbuffer context12 binding/PB_SETOUTER commands captured,
not a complete executed command trace or256MiB RAM grant.

Initial274 worker state6/reason14: CPU0 epoch1 acknowledged4 live callbacks;
accounting/shader unknown/pending0. No observer arm, terminal boundary or reuse
draw. Four disabled refs2/cache1/unit1 and21bindings in partial3584rows.
Host unbounded atomic replace inherited272 then failed Windows sharing error5
while reading page14:14/218 initial pages retained. UI capture complete. This
host failure is separate from the earlier real refusal. Breakpoints removed,
physicalmode0, frontend reopened, quarantined guest, orderly host exit0 without
fallback. No normal guest terminal/Windows shutdown claim.34 private captures,
72 frozen dependencies exact; QCOWclean/EEPROMsame. Strict disk equalityFALSE:
1byte reservedsector1536, full8GiBmapping/65536overlay prove filesystem bytes
inherited unchanged, writerunattributed. Host173checks163mutations plus15actual
RAMHTchannel mutations rejected. No performance/GPU/physical qualification.

NEXT: do NOT rerun same binary to get callback rows. Exact274 source appends
kind17 only AFTER zero-count gate/secondCPUboundary, so refusal pages lack them.
Implement NEW bounded READ-ONLY terminal-refusal CPU inventory property on
exact274, acquire terminalstate/CPUdone with immutable epoch/thread/time/reason/
count and complete identities/ranges. No new jobs/clearing/arm/release/joins or
gate change. Test early publication/capacity/identity/transport negatives.
Use existing tested bounded atomic_json writer (surface-bridge260) in the NEW
controller, test real transient and permanent Windows sharing; retain275's
unbounded writer/failure frozen. Only then distinct observation-only fresh
standalone child with same271 XBE may capture fullgraph+callback identities.

Physical audio004/softwarevideo118/shared158/FATX0101 unchanged. No hardware
test queued. Keep all previous recovery/release/strict limitations below.
C last21579042816bytes, E40562065408bytes; preserve20GiB guard, inspect capacity.
No backing chains moved. New portable/scratch onE through supported roots.

--- Previous continuation (preserved) ---

'''
assert not p.read_text().startswith('#275 CLOSED');p.write_text(prefix+p.read_text())
print('Recorded closed275 continuation and exact callback source finding')
