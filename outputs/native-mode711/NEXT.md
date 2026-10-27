#711 CLOSED: baseline-only call returned GREEN held checkpoint

Read observation001, collection001, audit001 and closure001. User reported GREEN
holding, then confirmed manual power-cycle. Nine new reports collected once;
PCI/CRTC/SEQ/geometry/allocation mappings equal710. Independent aliases and
source/binary/report pins pass. No hook/host child, console at dashboard.
No repeat launch/recollection of711 or closed708/709/710.

Next NEW712: review and host-validate a tightly bounded blank-and-restore-only
probe using the checked baseline. Before any launch, verify the exact original
sequencer state, PCI/decode obligations, retained704 blank/output-enable source
and restoration ordering. Save/restore indexed selectors and the exact admitted
sequencer value. No encoder, geometry, timing, clocks, interrupt-pending changes
or speculative functional patch. Do not silently import firmware state.

Design a finite native PM delay and a distinct optical result after restoration;
if output cannot be restored, do not retry or claim completion. Since a black
screen loses framebuffer observability, preserve that limitation and assess
whether an independently qualified status path is needed before admission.
Test exact linked/relocated instructions, timer failures, restore/no-retry paths,
forbidden writes, stack/ownership and whole framebuffer guards in fresh fixtures.
A source/model PASS is not physical output-gate proof. One watched attempt only.

711 qualifies only the baseline return on this run; it neither fixes nor proves
the precise failure location of708/709. Preserve both failures. No native mode
initialization or Windows1.6 qualification yet. Hardware ticket retained;
build/xemu released; automation paused; original720p protected, console C off
limits. Other work remains tabled.

Reconstruction: source-preservation001.json contains exact executed gpu_legacy.c
and gpu_types.h bytes. Public files have whitespace-only normalization after the
publication check rejected inherited formatting. Build receipts are unchanged;
verify executed hashes through that snapshot, never waive mismatches or rewrite
old records. Restore into fresh private inputs if reusing this source lineage.
