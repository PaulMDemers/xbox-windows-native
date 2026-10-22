#649 CLOSED: review status semantics and video timing before a functional change

Read REPORT.md and actual launch/user-observation/collection/audit/closure001.
Second flashing amber + third flashing green map to wait3 and3M..36M raw ticks.
Same phase class as648; these are separate instrumented runs. No exact timer or
status-byte receipt. Consistent timer assumed; not a physical wall-clock proof.
All28 selected files unchanged, no new events/6006; normal720p/startup exact.
No hook, rollback or owned process. Isolated candidate files retained. Dashboard
reachable.649/648/647 CLOSED: no repeat launch, recollection or runtime reuse.

Next perform a static review using pinned source and primary register evidence:
- Verify what GPU offset0x6013da bit3 represents on the selected head and which
 display-timing/enable state governs it. Do not conflate a status-bit value with
 physical scanout or a latched interrupt. Identify documented read side effects.
- Decode the intended633480p CRTC/extended timing fields and compare with the
 existing source programming sequence,720p profile and qualified retained evidence.
 Separate programmed constants from actual readback. Track retained VPLL/PCRTC
 state and timing-update handshake as unknowns; never borrow firmware values.
- Review whether later encoder/DAC/unblank writes depend on completing the poll,
 so that a proposed observation distinguishes a circular dependency from a timer,
 status-source or timing-programming problem. Do not assume one is the cause.

If the source review identifies missing physical facts, prepare a NEW bounded
readback diagnostic with documented register semantics and a clear interpretation.
Capture pre-write versus post-write state separately, using already-observed data
where possible. Validate sampling/decoding and exact compiled code on the host
before staged-byte verification and a watched launch. Use new kit/paths and leases.
Keep detailed-state observability limits explicit; LED categories are not dumps.

No timeout expansion, early-success fallback, pending-bit clearing, interrupt or
clock-state borrowing, validation waiver or speculative driver/profile patch.
No extra hardware launch is queued. No diagnosis of645, boot-reliability fix,
live switching, other-revision or acceleration promotion. Automation stays paused.
