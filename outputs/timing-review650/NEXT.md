#650 next: expose actual status and masked readback in a new diagnostic

650 is a static review, not a console attempt.649/648/647 remain CLOSED. Never
rerun/recollect them. No functional480p fix has been identified. Read REPORT.md,
decode001.json and the latest continuation first.

Prepare NEW651 from pinned633 plus reviewed649 instrumentation, keeping profile,
poll predicates/limits, output-control ordering and ordinary720p unchanged.
Use a new owned path and attempt ID. Do not stage or launch before host admission.

Required observations, separated by capture point:

1. Before any functional writes: retain original VPLL/PCRTC_CONFIG observations
   and existing handshake samples. Add only qualified readable timing storage.
2. After the functional setup returns, before any LED or reset action: capture
   the same readable CRTC/FP subset already used by631; preserve selector state.
   Mark success versus error and phase. A timeout snapshot is not an atomic
   pre-timeout snapshot. Capture existing0x6806a0 read with request/ack bits raw,
   labeled tentative handshake interpretation, not a new completion predicate.
3. Reuse the six existing edge records: wanted, first/last byte, count, byte/bit
   changes, completion, raw timer delta. Do not add another status read just to
   classify the existing failed wait. Expose whether the failed wait was a
   constant0xff, another constant byte, or varied; first/last alone cannot prove
   every sample was0xff, so use samples/changes or an explicit count.

Prefer bounded post-result LED summaries for (a) actual status class, (b) masked
CRTC timing match, (c) FP timing match, and (d) request/ack equality. Keep invalid,
not-captured and I/O-failed states distinguishable from a match. Publish the exact
observable mapping before a watched launch; detailed RAM fields are not durable
receipts. Limit the watch burden; do not claim a bitmap was observed from a color.

Use631's23 CRTC indices and established masks (CR19=e0, CR2d=01);14 FP fields
plus general-control0x680600 already have retained stock readback. Do not expand
into undocumented counters, interrupt/status-clear registers or encoder reads.
CR41 is unobserved in631 and remains outside that proven subset. Additional
SR1/index access needs explicit semantics and selector preservation review.
Do not silently change interrupt state to take a snapshot. If safe selector
access cannot be established at native entry/return, narrow the probe or stop
its admission rather than assume the stock kernel's context applies.

Host gates: differential original callback ordering excluding declared added
reads/selector accesses; exact limits; every mismatch/unknown category; selector
restoration with non-default indices; existing trace classification for all
byte values and transitions; compiled wrapper/adapter access review; source,
compiler, binary and staged-byte pins; output/WSL backing20GiB reserve and leases.
Preserve any failed build/review. No new VM/disk required just to validate helpers.

On admission, use new physical baseline/ownedEpath and one SITE with20s reply
bound. Existing authorization permits launch; obtain screen-watch readiness only
if needed. Keep normal720p/startup protected and use no startup hook. Observe one
bounded return; do not repeat accepted/uncertain launches. Collect once and audit
selected hives/events/files. No timeout extension, pending-bit clearing, firmware
state borrowing, early-success fallback or speculative timing rewrite.

Interpretation: mismatched readable timing motivates investigating write/latch
behavior; matching timing leaves clock/routing and effective status progression
unresolved. Equal request/ack is only a sampled value. Constant0xff is suspicious
but not proof of unmapped MMIO. No category alone establishes a repair.
