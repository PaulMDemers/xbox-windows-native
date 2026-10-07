# Next implementation: framebuffer ownership handoff, UC control first

Both cases are CLOSED: video-cache-contract/trace001 failed observer coverage,
then passed resumed workload/cold gates; this kit's trace002 passed its mapping
diagnostic and cold gates. Never relaunch/recollect them. Read REPORT.md,
contract-verification.json and map-replay.json. No owned process remains.

The simple boot-time WC flag candidate is rejected: the real NT5 function rejects
WC at the observed bootvid state. Do not set MiWriteCombiningPtes, rewrite kernel
code, change global PAT/MTRRs or rely on a desktop-only WC mapping. Another
identical MSR/row-copy run has no useful discriminator.

Build a reviewable framebuffer ownership interface before a speed candidate:

1. One provider owns the reserved4MiB mapping and bootvid's hidden backbuffer.
   Early boot uses UC; initially keep the proposed handoff UC too. Give desktop
   consumers a counted lease rather than a second independently chosen physical
   mapping. Pin the bootvid/miniport interface ABI and check real NT5 loader/import
   support before assuming a new cross-driver call will link or load.
2. Prove a quiescent handoff after boot-video relinquishes display ownership,
   with no outstanding bootvid reader, no legacy alias access and correct IRQL.
   InbvNotifyDisplayOwnershipLost/InbvCheckDisplayOwnership are installed exports
   worth reviewing; ownership state alone is not a lock or a proof of quiescence.
   Examine their installed implementations and the real callback order before
   selecting the hook. A cold desktop snapshot does not settle this race.
3. Define failure and crash behavior during handoff: no reader may retain an
   unmapped pointer, no bugcheck renderer may wait on a lower-IRQL owner, and
   mapping failure must leave a usable UC fallback without mixed UC/WC aliases.
   Prove consumer stop/restart and final-shutdown behavior; retain direct RAM
   access after PCI aperture loss. No new allocation at crash time.
4. Test the ownership protocol with actual compiled code and hostile ordering,
   then a fresh ordinary unchanged-UC control with full drawing/cold/event gates.
   Only after this works, add a coordinated UC-to-WC transition in a fresh
   candidate through supported mapping APIs, with explicit write ordering and
   full alias/scanout checks. Do not call UC fallback a successful WC trial.

If a safe single-provider handoff is too invasive, choose the separately designed
cached-shadow display driver instead, with an explicit RAM budget and ordered
dirty copies. Do not substitute a collection of cache flags for ownership.
Review the saved POLICY.md (pre-run proposal) in light of these observed results.

Physical access remains outside this emulator-only task. Keep physical0101/
video0093,0088rollback,0.1.0 and all failure evidence; use fresh frozen IDs and
the20GiB build guard. Do not repeat successful128GiB dump tests. Real hardware
cache behavior and dragging performance remain future qualification gates.
