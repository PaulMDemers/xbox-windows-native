# Narrow final cache-owner disposal proposal

282 proves removal of four disabled unit references and normal unchanged guest
reuse, but leaves their cache references and GL names alive. The next distinct
operation may evict exactly these four cache owners after their unit references
are gone. No whole-cache flush/finalizer, renderer switch, reset, borrowed firmware
objects or host binder is an acceptable shortcut. Unrelated cache entries, dirty
surfaces, callbacks, scanout and actor owners remain untouched.

The helper is a HOST-ONLY proposal. It uses the exact original LRU eviction,
cache post-evict callback and counted destructor. A NEW actual proof provider
must supply complete locked post-unit-release graph, current contexts/UI edges,
worker/CPU acknowledgments, guard disjointness and successful post-unit snapshots.
The existing actual stage2 refs1/cache1/unit0 contract is validated without fake
refs or epochs. The provider and full four-boundary worker are not implemented.

Find each binding only via its current live cache edge, then validate sole ref,
GL name/target, immutable source/palette key and no dirty/enabled/unit edge. Refuse
a pre-eviction callback because calling lru_evict_node directly would otherwise
bypass its veto. Require the exact original post-eviction callback. Selected cache
nodes persist, whereas TextureBinding pointers die; never dereference saved
bindings after final release. Actual glIsTexture must become false and errors
must remain clear. Partial mask is exact and quarantines; never fabricate rollback.
An accepted disposal has actual counted final-free records, not just cleared slots.

Runtime integration needs a NEW four-boundary protocol: pre-unit release,
post-unit release before cache disposal, post-disposal before guest resume, and
post-resume replacements. Each boundary requires fresh real CPU/context proof.
The missing old cache/unit/binding rows after deletion must be represented
explicitly, never encoded as refs2 or fabricated identities. Keep initial records
immutable and overall transaction state authoritative. No legacy actor reset.

Observer design must keep old-generation tombstones, record actual final frees
before original destruction, and separately record real creation/replacement
generations and actual normal guest binds. A new allocation may reuse the same
numeric address or GL name; those are not old generation survival. The current273
four-watch same-live-generation schema cannot qualify deletion/replacement as-is.
Require actual original generation/upload lifecycle instrumentation and independent
source/key/RGBA/framebuffer/guard evidence after resume. No new runtime should be
launched merely to observe known fields; finish this protocol and host tests first.

GL namespace deletion is not a native Windows GPU ownership grant or proof of all
backend resources retired. Retain finite fences, error unions and postmutation
quarantine. Native PTE/cache aliases/deferred release remain separate.
