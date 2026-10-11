# Latest-surface preservation discriminator

Read-only review of the actual247/build004 capsule surface.c; no graphics code
changed in249/250. Existing244 event2/3 covers the common invalidation lifetime,
but247 events82/83 only wrap flush_surfaces and observed no entries in247/248.
Earlier227 readback is a checkpoint, not proof of bytes at later invalidation.

Five direct call sites in the pinned surface.c:

| Caller | Line | Current behavior before common invalidation |
| --- | --- | --- |
| invalidate_overlapping_surfaces | 517 | download_if_dirty |
| surface_evict_old | 616 | download_if_dirty |
| pgraph_gl_process_pending_downloads | 926 | blocked CPU-store path, download/assert draw clean, update bindings |
| update_surface_part incompatible surface | 1339 | download_if_dirty |
| flush_surfaces | 1580 | download commented out; current82/83 only here |

These are source observations within this capsule, not proof of runtime coverage
or a whole-tree reference census. Inspect exact call/context/lock ownership again
before editing. Common pgraph_gl_surface_invalidate begins574, queues CPU callback
removal594, deletes GL texture596 and unlinks/frees the surface598/599. Observe
latest object, callback, range, bindings and four flags before those operations at
the common entry, with distinct caller reasons where available; avoid stale
pointer reads after free. Flags must not all be described as GPU dirty.

For a NEW measured bounded run, require actual dirty and clean invalidation
coverage, before/after byte identity using an independent controlled pattern,
both CPU-read and CPU-write alias activity, and correct primitive/pending state.
Scalar flags/fence success alone do not establish contents. Do not unconditionally
download old GPU contents onto newer CPU data to cure the commented flush path.
Refuse conflicting ownership rather than guessing. CPU-store path424 waits for
downloads after dropping PGRAPH; it sets upload_pending and sometimes eviction
while the original store is blocked. Other paths need their own actual ordering.

No new GL deletion, callback retirement, shader-save join, shared reference unbind
or native GPU permission follows from this review or the worker/UI barriers.
