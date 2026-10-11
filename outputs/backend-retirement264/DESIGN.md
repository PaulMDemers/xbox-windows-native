# Proposed bounded old-backend retirement transaction

This is a design, not implemented permission to submit native GPU work. First
implement the read-only ownership ledger in NEXT.md. The present263 range
inventory cannot authorize a whole-backend mutation.

## Scope and continuing owners

Keep the native258 allocation/FileObject until reboot, unchanged guest drivers,
the actual guest framebuffer reservation and guest PCRTC/PVIDEO/PFIFO/PGRAPH
register state. Never borrow firmware RAMHT objects/channels, reset the GPU,
advance global frame time, clear pending flags or fabricate an idle/granted state.
The intended transaction retires old SOFTWARE backend consumers, not hardware
ownership. It must restore a usable software backend before normal guest resume.
Guest page-table/cache alias validation and deferred native releases are separate
future requirements. A subsequent16x8 native copy still requires its own contract.

| Family / owner | Existing real disposal path | Required proof before/after |
| --- | --- | --- |
| Surface list, color/zeta bindings | surface_download_if_dirty; unbind_surface; surface_invalidate | Complete format/extent/content ledger; preserve latest bytes before flush; exact callback identity; attachment detach, list removal and GL deletion; CPU unlink/free acknowledgment |
| Texture cache + unit references | texture_binding_destroy; texture_cache_entry_post_evict; finalize_textures | Ledger keyed by binding identity with cache edges and all unit edges; refcnt must equal counted owners; owner unbind/decrement unit references before cache eviction; final count/deletion once |
| Palette source ranges | Same TextureKey/cache owner as texture | Preserve range identity; no invented independent palette GL owner; reject any unknown separate binding |
| Cached/inline/full-memory vertex data | finalize_buffers | All51200 buffer names plus current VAO/attributes/EBO/ARRAY bindings, not only93 live nodes; remove context/container references before deleting; no CPU readback needed for copies unless an actual GPU write owner is found |
| Scanout/display and overlay | finalize_display; UI framebuffer loan/release; PCRTC/PVIDEO and VGA remain | Drain UI consumers and both backend contexts; detach backend display/PVIDEO textures; preserve guest framebuffer reservation and verify software fallback/recreated output; do not zero guest scanout |
| CPU callbacks | mem_access_callback_remove_by_ref -> queued CPU exclusive unlink/free | Actual per-reference request/unlink/free plus a later acknowledged CPU-exclusive inventory; keep NV2AState/r alive until that inventory; work_list empty alone is insufficient |
| Additional backend objects | reports/shaders/render-to-texture finalizers | Complete report results and active query handling, shader reader/writer acknowledgments, all shader/buffer/FBO/container names and both context bindings; prevent new work during transaction |
| Additional UI consumers | HUD g_tex; snapshot display_tex; current GL bindings | Owner-side generation revocation plus no queued screenshot/thumbnail using retired generation; readback acknowledgment, context unbind and finite fence, not just framebuffer_in_use==0 |

## Phases and lock ownership

Every record carries a fresh immutable attempt/epoch, actual actor thread/context
identity, source and binary pins and bounded capacities. Duplicate requests,
stale generations, overflowing ledgers and unknown objects refuse. Old246/247
one-shot actors must not be reset: a future bridge needs new acknowledged epochs.

1. **Admit and freeze producers.** At the actual native checkpoint, verify the
   full IDT/kernel/process/driver/handle/four-page attestation. Stop guest execution
   and close ordinary guest command admission while preserving original state.
   UI completes its current frame and returns its loan. PFIFO remains alive to
   service real pending downloads/reports; never park the worker and then wait
   for a CPU callback whose completion needs that worker. Bound the natural drain;
   unsupported/persistent pending state refuses rather than being cleared.

2. **Acknowledge all actors.** UI thread revokes the old generation from HUD,
   screenshots and thumbnails and records its exact retained bindings. Drain
   already-issued requests before revocation commits. Keep the window alive with
   an independently owned presentation/fallback plan; replacing a borrowed ID
   with another alias of the same old object is not detachment. PFIFO fences the
   render and display contexts separately. CPU executes an exclusive inventory
   after prior work; never infer completion from queue emptiness.

3. **Freeze and validate an ownership ledger.** Under the necessary locks, walk
   all seven range families plus unit/binding/refcount edges, allocated GL names,
   both context containers, report lists, shader threads and UI holders. Read
   bindings in their actual owning context. Active primitive, unknown vertex
   span, incomplete report, unacknowledged shader actor, unexpected framebuffer
   loan or unstable epoch refuses before mutation. A cache key points at guest
   memory; it does not imply that its GL object is the latest writable owner.

4. **Preserve latest data before ANY flush/finalize.** Determine writer provenance
   for each actual surface. Dirty GPU data with no conflicting completed CPU
   writer must download and compare with an independent readback. Clean surfaces
   with upload intent preserve CPU RAM; do not download stale texture contents.
   Dirty+upload is not universally invalid:263's blocked-store case had it while
   the CPU write was still waiting. Whole-backend retirement must first drain
   that real path, then take another coherent inventory; an unresolved conflict
   refuses. No debugger read of dirty RAM before the intended CPU access.
   Verify all dirty color/depth/swizzled/multisample formats actually present;
   unsupported formats refuse.263's13x11 BGRA8 proof is not blanket format coverage.
   Keep a pre-disposal content manifest and independently check cold bytes/guards.

5. **Retire real owners in order.** Only after all preconditions are acknowledged:
   detach UI/display sampling and framebuffer attachments in their contexts;
   detach active render targets; release unit texture references with the real
   decrement helper, then evict caches; invalidate preserved surfaces through
   the real callback-removal path. Detach VAO/buffer references and dispose the
   actual backend copies. Complete reports, never delete pending results as if
   delivered. Complete/join acknowledged shader jobs before freeing their memory.
   Dispose owned display/shader/FBO objects only after all external consumers
   are revoked. A new bounded wrapper must expose failure; existing finalize
   routines are not callable wholesale until their early-return/leak/drain paths
   meet these preconditions. Do not restore retired GL names as "binding restore."
   Restore only still-owned unrelated state, or bind newly created owned objects.

6. **Post-acknowledge and audit before freeing backend state.** Release renderer
   locks before the CPU-exclusive post inventory. Require old callbacks absent,
   all their real unlink/free events complete and actor generations still closed.
   Require all removed binding owner counts zero and deleted names absent from
   every relevant container/context. Keep r and callback opaque state alive until
   the last dependent acknowledgment. A transient all-zero scalar list is not
   proof of GL object destruction. Hash all promised preserved RAM; compare
   guest register/channel/object state with the pre-transaction image.

7. **Recreate and resume a software owner.** Initialize a fresh backend generation
   from preserved CPU memory and explicit state, verify its display output against
   an independent oracle, then return the new frontend loan capability. Resume
   the guest only after that succeeds. No native GPU grant is published. Run the
   normal workload, normal restart, orderly host close, full cold allocation/hive/
   protected-hash/byte/event audit. Keep strictFt49 separate and unwaived.

## Locks, deadlines and irreversible failure

Existing normal framebuffer get holds renderer_lock, then takes FIFO and may wait
for PFIFO sync. The new admission must close that UI path before worker-side
FIFO->TRY(renderer)->TRY(PGRAPH) inspection. Never turn those trylocks into
blocking reverse-order acquisitions. Existing callbacks hold PGRAPH only while
marking, then release it before FIFO kick and download wait. Preserve that rule.
Shader workers can need shader_cache_lock: never join them while holding it.
No actor-completion wait while holding BQL/FIFO/PGRAPH/renderer/work_mutex or a
lock required by the completing actor. Short coherent snapshots can use the
263 trylock scheme; release locks before fences/CPU acknowledgment/waits, then
revalidate the transaction epoch. A stopped vCPU still services exclusive work.

Proposed initial bounds: one operation/attempt;128 surfaces,512 texture nodes,
51200 element nodes,256 CPU callbacks; explicit per-context allocated-name and
shader/query capacities determined from pinned structures; no silent truncation.
Reuse finite100ms context fences and a10s transaction deadline only as INITIAL
limits, not promises that a host GL driver call can be interrupted. Ordinary
GL download/delete/driver calls can block; an external bounded supervisor may
terminate a sacrificial child, which is a failed interrupted run requiring its
own cold audit, never orderly success. Thread joins require a completion flag
first with bounded polling, then join without locks; absence of that flag refuses.

Before first mutation, refusal may restore the previous admission state only
through the real actors and acknowledgments. After partial disposal, do not
pretend rollback succeeded, resume unsafe objects, reset the epoch, or retry in
place. Preserve trace/disk, close the owned child, audit as interrupted and use a
new immutable fixture for any revised experiment. Only the complete software
recreation phase permits guest resume. No physical run is implied by this design.
