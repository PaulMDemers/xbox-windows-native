# A bounded release of four disabled unit references

This kit contains a proposed narrow helper and host tests only. It is not applied
to xemu or a native driver. It does not dispose a cache object, run a whole
finalizer, join shader threads or grant native GPU ownership.

The267 observation found four distinct disabled units, each with one cache
reference and one unit reference. Only one remained bound in its matching render
context/unit. The proposal accepts that shape only: four distinct 2D objects,
refcount2, one cache edge, one unit edge, no unknown owner, pending work, callback,
overflow, foreign-context/unit or container edge. The caller must build this
proof from a fresh coherent actual ledger under the reviewed worker/CPU/context
protocol; passing a fabricated struct is not an admission implementation.

Before any decrement, the helper rechecks actual unit identities, enabled bits,
refcounts, cache membership/count and current render-context 2D bindings. A bounded
512-node cache walk refuses cycles/excess entries. Actual binding queries must
match the supplied complete graph. It unbinds only a matching object's own unit,
calls the existing counted texture_binding_destroy exactly once per unit, clears
the unit pointer, and leaves texture_dirty true for the ordinary rebind path.
Each object retains its cache reference, so no GL deletion may occur. The active
texture unit is restored, including failed preflight. An error after mutation
must quarantine the transaction; it must never pretend to roll back by inventing
refcounts or resume under a PASS label. No such error was injected in host003.

Host003 executes the exact pinned pgraph_gl_bind_textures, counted destruction,
cache initialization/comparison/eviction and real QEMU LRU/queue code. Registers,
VRAM dirty queries, texture generation, parameter application, data hashing and GL
are explicit models. Model texture bytes are checked against independently
computed expected source/palette values. This checks branch/lifetime accounting,
not actual OpenGL pixels or guest execution. Surface-to-texture paths deliberately
assert if invoked and are outside this narrow model.

Cases cover indexed/non-indexed data; clean, dirty-but-unchanged, changed texture
and changed palette; unchanged control versus proposed release; and retained cache
versus later ordinary cache eviction. A released object is reacquired through the
actual cache lookup path, retaining the same identity without an upload when its
data and cache entry are unchanged. Changed data or missing cache causes the
ordinary upload/replacement path. Refcount checks use actual cache-plus-unit edges.

The original disabled branch only unbinds four GL targets and continues. It does
not decrement a unit reference or mark its unit pointer dirty. Consequently,
after ordinary cache eviction, a clean original unit may take the fast path with
one unit-only reference. Host002 incorrectly expected refcount2 in that control
case and failed. Host003 corrects the independent expectation; the original code
and proposed release helper are byte-identical between002 and003. Host001 failed
compilation for a missing model constant and misleading indentation. Both failures
and exact private inputs remain preserved.

The source reset path requests pgraph flush and clears registers; the GL flush
marks texture data possibly dirty but does not flush the texture cache or clear
unit references. This permits, but does not prove, cache identity reuse after a
normal restart. A desktop, FTP response or unchanged arena is insufficient.

## Runtime discriminator before any release

Use a NEW read-only control child of exact267, with no release helper installed.
At the existing attested Windows checkpoint, discover the four actual units and
record immutable owner generations, cache keys/shapes/data hashes/draw times,
actual GL object/context identities, bounded raw texture/palette source bytes and
canonical RGBA readbacks. A renderer data_hash alone is not a collision-resistant
source-byte identity. Preserve
the readback bytes privately and compare them independently on the host. Reject
unsupported formats, over-capacity images or incomplete capture. Readback must
save/restore texture selection and every pixel-pack/PBO state it changes, use a
finite owned context boundary and never alter guest buffers or PFIFO commands.

Add bounded observation at the actual normal bind/cache replacement/free sites.
Watch generations, not raw pointer or GLuint equality: an address/name reused
after destruction is a different object. Publish immutable records only after
the actual work at each site. Never dereference a watched freed pointer. Normal
guest restart/return may then produce real binds. Require an actual guest-driven
bind of an original still-live cache object with unchanged key, data hash and draw
time, byte-exact source/palette equality verified independently on the host, and
exact readback equality to its independently preserved pre-resume bytes.
Changing source data makes that particular equality case inapplicable, not a
license to ignore it. A deleted/replaced object is not a reuse success.

If the unchanged control does not naturally cover those identities, record failed
coverage and stop using that workload for release qualification. Choose an owned
guest graphics workload which actually reuses its own textures; do not manufacture
guest commands, borrow firmware channels or directly invoke the binder from the
host and call that guest reuse. Only a qualifying control supports a matched new
release candidate with identical observation and complete before/after graphs.
Readback equality proves texture-content preservation, not final-frame visual
correctness or a speedup; keep those claims separate.

The previous UI metadata lock has no independent acquisition deadline. Review its
main-loop/BQL order before extending that boundary. Existing267 single-use actors
cannot be reset for a second snapshot. Keep immutable new epochs, complete bounded
storage, CPU/worker/context acknowledgments, normal shutdown, orderly host exit
and full cold audits. Ftdisk49 remains a strict failure. PTE/cache alias handling,
deferred native release and the continuing scanout reservation are separate.
