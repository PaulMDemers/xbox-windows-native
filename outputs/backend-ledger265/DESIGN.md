#265 read-only ownership observation

This diagnostic implements part of264's ledger phase. It does not dispose any
backend object, revoke a frontend holder, join a shader thread or grant guest GPU
ownership. It is deliberately separate from263's renderer-pattern experiment.
The historical emulator fixture is not the audio-integrated physical demo.

## Native identity and unchanged CPU data

The new probe uses unchanged258's reboot-held16KiB allocation and GENERIC_WRITE
FileObject. It reads and checks the original CPU seed before and after the host
observation: two reads, zero writes,32768 exact bytes. Each of two checkpoints
requires actual IDTR-derived kernel identity, resident kernel/driver/probe code,
process/handle/object ownership, generation and four page translations. No host
read of the arena payload, guest memory write or register write is allowed.
The probe locks only its own first4KiB image header for identity inspection.

## Actor sequence and publication

The actual UI thread closes the existing one-shot246 gate and records its own
SDL context, HUD/snapshot retained texture names and current GL bindings. Its
immutable rows publish through the existing release/acquire readiness flag.
It does not substitute or revoke a texture. Reopening uses246's ordinary one-shot
path; neither246 nor247 is reset.

A single capture, epoch1, requires stopped guest CPU, closed UI, OpenGL and unused
260/247/227 actors. The existing PFIFO worker owns the collection. It temporarily
halts producer admission, releases FIFO while CPU-exclusive jobs run, and waits
for actual before/after acknowledgments. An empty work queue is not completion.
Finite render/display fences run without FIFO/PGRAPH/renderer locks. These create
and delete temporary GL sync objects; they do not flush a guest surface/cache or
delete a backend resource. Context selection returns to the render context.

PGRAPH and renderer locks are acquired by bounded refusal (trylock). Nine pending
predicates remain refusal conditions. The shader-cache lock protects collection
against its loader, but completion of the loader and save-thread handles remains
UNKNOWN. A nonnull save-thread handle prevents reading its concurrently freed
program buffer. No thread handle is equated with a joined thread.

The renderer captures cache-node, unit, binding/refcount edges, including unit-only
bindings; all51200 allocated element-buffer names; fixed/inline buffer, VAO, FBO,
program and texture names; shaders/modules and query reports; continuing scanout
and overlay registers; context bindings and vertex attributes. Free-node keys and
clear-only query fields are not read because ordinary constructors do not
initialize them. The two acknowledged CPU callback inventories must be identical.

## Bounds, transport and failure

Renderer metadata is capped at180000 rows of eight64-bit fields; UI metadata at
8192. Limits are explicit for bindings516, cache512, surface128, query4096,
reports128 and existing51200-element/shader caches. Overflow latches and refuses;
it is never a complete observation. Unit/target selection is restored after each
context query. Worker deadline10s, UI capture1s, GL fences100ms each. External
supervision also bounds transport and orderly host cleanup.

Immutable data is retrieved in256-row pages after terminal publication. Page,
epoch, total count, capacities, unique row indices and hashes are independently
checked; first pages and terminal report are reread for immutability. Partial
failed observations are preserved. Success restores original PFIFO halt state;
failure quarantines the attempt until owned exit. No failed disk is repaired,
relaunched or used as a parent.

## Limits retained for later work

This is a bounded observation, not comprehensive retirement proof. Shader actor
completion remains unknown, indexed buffer bindings and GL container attachments
need separate closure review, and continuing UI/scanout references are not revoked.
Texture reference accounting can validate only the recorded cache/unit graph.
No actual texture leak follows from a unit-only binding or a retained reference.
Guest cache/PTE aliases and native deferred release remain separate requirements.
Normal guest restart, orderly host exit, full allocation/hive/protected-file audit
and unchanged strict events are required after observation. Ftdisk49 is retained
as a strict failure, never suppressed or relabeled.
