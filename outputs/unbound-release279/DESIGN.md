# Unbound-only unit release proposal

279 is a host-only proposal. It is not installed in xemu or a native driver.
278's closed no-release control supplies actual unchanged guest reuse coverage;
it does not supply release coverage. The new proposal is deliberately narrower
than 268: all four selected textures must already have no GL binding, FBO edge,
UI holder or current VGA surface use. Any such edge refuses. It does not unbind
an object from an unknown context, nor call a renderer-wide finalizer.

`review.py` validates the complete recorded 278 scalar ownership proof and the
separate graph/context/actor parsers, then checks all selected owners against
every captured texture binding, known FBO attachment, HUD/snapshot/last holder
and current VGA DisplaySurface. It additionally ties UI container headers to
the independently recorded current-context integer bindings. The scope remains
the pinned GL4.0 interfaces and known backend/current UI containers, not every
extension or unknown object. The actual 278 control contains no selected edges
in that scope. Live runtime must reproduce this evidence, not reuse old names.

The new `X279Proof` contains an unchanged X277 observation proof and an explicit
release operation plus additional current graph/owner/lock/context conditions.
X277 still rejects its own release_requested flag and validates its actual
nonzero callbacks, mutation clock and whole-allocation disjointness. X279 uses
that proof as evidence of a completed observation boundary; the new operation
is separately authorized by its additional contract. It never passes a fake zero
callback count into 268/274 or modifies their gates. Boolean admission inputs
are not a runtime adapter: current host fixtures model them explicitly.

`x279_release` rechecks all four live units, disabled bits, exact owner/name/
refcounts and actual cache keys/edges before any decrement. A bounded cache walk
requires one cache owner per object and the exact recorded live count. Current
render-context 2D bindings must all be zero; active texture selection is restored.
The complete multi-context graph requirement is separate from that local reread.

Mutation calls the actual counted texture_binding_destroy, including the actual
278 observation hook. It then clears only that unit pointer and sets texture_dirty
for the original rebind path. Cache entries, source/guard bytes, dirty surfaces
and all callbacks remain untouched. No refcount is assigned, no texture data is
uploaded/downloaded, and no GL deletion should occur because the cache retains
one reference. Each completed mutation sets an immutable-result bit. A GL or
observer error, or unexpected remaining refcount, returns QUARANTINE with the
partial mask; never restore refcounts or resume as successful after that result.

## Required integration before a build or guest

Use a NEW exact278 child with its own opt-in request and one-shot owner state.
Preflight and preallocate bounded immutable pre-release and post-release graph
storage before mutation. Arm generation observation only after the full actual
pre-boundary proof. Keep the same PFIFO owner, stopped guest, closed frontend,
finite context fences, actual lock ordering and complete callback inventories.
The live worker must derive all X279 inputs from actual observations; it cannot
load the host fixture or infer complete ownership from a count.

After release, capture an immutable full graph: four null unit pointers, four
live cache objects with refs1/cache1/unit0, identical keys/names/source snapshots,
no new GL/UI/container edges, unchanged unrelated owners and unchanged callback/
surface tuples and clocks. Require fresh acknowledged CPU boundaries around the
post-release capture and recheck. After normal guest resume, capture a third
full graph and verify each same generation reacquired its unit reference with
exact independent source, RGBA and framebuffer bytes. Only then seal the terminal
accounting on the owner worker. Expected release-related decrements must be
explicitly distinguished from the subsequent normal guest bind events.

This needs a NEW explicit epoch protocol for pre-release, post-release and
post-resume stages. Do not reuse initial/end actors or fake old epoch numbers.
X277 expects refs2/unit1 and epochs tied to its two old stages; it cannot validate
the actual post-release refs1/unit0 state. Implement and test a separate post-state
contract, or a reviewed split of common boundary validation, without rewriting
observed fields to fit the old validator. Missing post-evidence quarantines the
mutated run. Actual worker lock/publication sequencing, three graph transports
and their independent parser negatives remain unimplemented in 279.

Two dirty surfaces' native provenance remains unresolved. They remain outside
this narrow texture operation, not evidence of backend retirement. Native Windows
PTE/cache aliases, deferred release, UI holders and scanout ownership remain
separate before any native 16x8 copy or GPU grant.
