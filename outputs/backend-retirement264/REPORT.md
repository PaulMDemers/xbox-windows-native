#264: backend retirement source review

The completed263 pixel discriminator does not retire the old backend. Independent
analysis of its four terminal inventories finds the SAME118 references at every
stage:24 texture-cache nodes,93 cached vertex nodes and one conservative scanout
tail. Their identities AND byte ranges remain equal, not merely their counts.
Forty mutations of the actual report reject missing/duplicate/unknown references,
out-of-RAM/arena-overlapping ranges, failed acknowledgments and pending state.
This is new analysis of closed evidence; no263 collection or guest run was repeated.

Twenty-six reviewed source files exactly match the263 build pin manifest.
Private snapshots are `E:/Codex-archive/xbox-windows-native/retirement264-source001`
and `retirement264-source002`. See source-review.json and source-review002.json.
The additional actual queue header used by the host test also matches that manifest.
The first capture preflight rejected nonexistent ui/xemu-gl.c before creating any
destination; the corrected closure uses the actual SDL context files. An initial
WSL rg command failed (rg absent, shell interpreted the pattern's pipes); it made
no changes. Subsequent source reads used individually verified files.

## Findings that change the design

1. **The ordinary flush/finalize path discards dirty surfaces.**
   gl/surface.c:1607 flush_surfaces explicitly leaves the download call commented
   out before invalidation. gl/renderer.c:83 finalize calls that path. Existing
   renderer switching calls flush before finalize (pgraph.c:3239 onward), so a
   late preservation hook inside finalize would already be too late.263 exercised
   age and CPU-store paths, not this flush path. Preserve BEFORE either operation.

2. **The texture finalizer drops pointers without releasing unit references.**
   gl/texture.c:375 increments a binding reference for a texture unit;:401 releases
   a replaced unit. The cache post-evict owner separately decrements at:785.
   But finalize_textures:816 only NULLs unit pointers before flushing the cache.
   Cache and unit ownership therefore cannot be treated as one reference.
   The disabled-texture path also unbinds GL targets without dropping its stored
   unit pointer; a disabled unit is not proof that its counted reference is gone.

   test-texture-lifetime.py compiled the EXACT three relevant functions and real
   pinned LRU/queue implementation with counted glDeleteTextures/g_free stubs.
   Twenty-eight ASan/UBSan cases cover0..4 units, shared/distinct bindings and
   a unit-only binding no longer in the cache. Original finalization retains the
   unit-owned objects; a host-only release-before-finalize sequence balances them.
   Deliberate retained objects were measured then explicitly cleaned up so the
   sanitizer checks the harness without discarding the measured failure.
   See texture-lifetime-test001.json. No renderer patch or actual GL deletion
   qualification follows;263 did not capture unit-to-binding/refcount identities.

3. **Frontend completion is not frontend reference retirement.**
   ui/xemu.c:981 stores the texture in both the snapshot and HUD consumers;:1003
   returns the framebuffer loan. ui/xemu-thumbnail.cc:27 retains display_tex and
   reads it during thumbnail creation; ui/xui/main.cc:65 retains g_tex and uses it
   for rendering and screenshots.246's closed actor gate fences/observes but does
   not revoke those consumer IDs. A zero framebuffer loan cannot stand in for
   owner-executed invalidation and an acknowledgment from the UI actor.

4. **The seven families describe guest-memory ranges, not every backend object.**
   The vertex finalizer deletes51200 allocated element-buffer names, inline and
   full-RAM copy buffers and a VAO, even though only93 cached nodes are live in263.
   Shader programs/modules/save threads and pending report queries also have
   disposal owners. Reports must complete their guest writes before disposal:
   finalize_reports deletes queued queries instead of delivering their results.
   Shader finalization can join background threads and perform disk I/O; its
   cache-disabled and file-open-failure paths do not establish complete draining.
   These are source-level gaps in a bounded retirement proof, not observed263 faults.

5. **There are at least three context roles.**
   PFIFO switches between render and offscreen-display contexts; the UI has its
   own SDL window context. Both backend contexts share GL objects with the UI.
   A fence in one context is not evidence that other owners unbound their names.
   The reviewed SDL glo_context_destroy frees its wrapper without an explicit
   SDL_GL_DestroyContext/SDL_DestroyWindow call. Do not use it as proof that all
   outstanding GL references disappeared. No context destruction is proposed here.

6. **Scanout is a continuing guest contract.**
   The263 scanout record covers PCRTC_START through the end of VRAM conservatively.
   Backend deletion does not change that PCRTC address or the VGA fallback reader.
   The current scanout reservation must survive a software-backend handoff until
   a separate guest/loader/display contract changes it. Do not claim all VRAM is
   free, clear display registers, or infer native GPU ownership from host cleanup.

DESIGN.md specifies owner order, finite acknowledgments, refusal conditions and
irreversible boundaries. NEXT.md makes the next implementation a single richer
read-only ownership ledger rather than another pixel replay or a blind finalizer
call. Full disposal is gated on that ledger and real owner acknowledgments.

## Actual state

No guest prepared or launched; no renderer/native driver changed; no physical
access. All264 host subprocesses closed.263 scoped preservation PASS and strict
FALSE/Ft49 remain exactly as recorded. Historical262 pending reason7 remains
unresolved. Physical audio004/softwarevideo118/shared158/FATX0101 and the verified
256 private recovery remain unchanged. No speedup, native GPU grant, complete
backend retirement, hardware qualification or new recovery bundle is claimed.
