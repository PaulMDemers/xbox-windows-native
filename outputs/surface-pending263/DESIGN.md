# Observe the actual pending condition

262emu003 refused stage1 with reason7 after the native ownership attestation and
CPU-exclusive pre-audit. No test surface existed. The existing report combined
nine predicates, so it could not identify which pending operation caused refusal.

263 records those same nine values under the existing FIFO, renderer and PGRAPH
locks. Bits0..8 mean waiting_for_nop, waiting_for_flip, waiting_for_context_switch,
renderer switch not idle, flush_pending, sync_pending, downloads_pending,
download_dirty_surfaces_pending and shader_cache_writeback_pending. The exact
OR condition still refuses reason7. The slot mask is read only after terminal
state is release-published and QOM acquires that state. It is never reset, and no
pending state is cleared or ignored. Host tests cover all512 combinations both
as booleans and full nonzero unsigned values under ASan/UBSan.

Only renderer.c differs from exact compiled262. The native probe/driver, four
renderer operations, bounded scalar telemetry, parser, callback retirement,
GL-state restoration, CPU inventories and seven reference families are unchanged.
The existing correct launch reply deadline and explicit host helper inventory are
retained. The new runtime copies the never-executed261 standalone seed; no failed
runtime disk is reused. All strict gates and the inherited historical emulator
device policy remain explicit, separate from the physical audio-integrated demo.
