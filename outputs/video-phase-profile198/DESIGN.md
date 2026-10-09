# Phase observation on the physical comparison's REP-copy parent

195 found only modest differences with scalar stores. This is an observation
experiment, not another copy optimization. Combine pinned170/113 phase timing
with pinned184/115, retaining both interfaces. XWN_UC_STORES is OFF in BOTH
builds; only XWN_BODY_PROFILE differs. All original drawing calls, returns,
surface ownership, clipping, row stores, cache attributes and modes remain.

Measure elapsed EngBitBlt, EngCopyBits, box row-copy body and whole upload
wrapper. Clock calls precede/follow the existing operations; the membership
semaphore protects aggregate accounting/snapshot only. No per-row clock or
logging and no lock held across rendering, copying or clock queries. The
existing submitted-PDEV lifetime contract remains necessary.

Reuse the actual170 arithmetic header and clock implementation; verify source
pins, ASan/UBSan boundaries, actual captured NT5 exports and resident compiled
sites.128 direct back-to-back query pairs, frequency, explicit errors and
saturating overflow flags are required. Calibration is not the complete
profiling wrapper cost. OFF retains calibration/common accounting/locks; ON
adds queries and tick/read arithmetic. Their difference is enabled profiling
increment, not all overhead versus an untouched driver. Do not subtract the
calibration minimum or claim exclusive CPU time. Upload wrapper nests body
profiling/bookkeeping; global elapsed counters include background/preemption.

New199 ordinary siblings use exact same settled181 parent and probe/guard.
Retain all65 pixel checks,25 timed loops and50 scanout comparisons, then add
200 real owned-window move/repaint/text/readback rounds. Confirm observed
phase/count/byte coverage and normal restart plus complete cold audits.
Emulator timing is not physical bus speed; no physical deployment here.
Physical0101/video0093,0088rollback,immutable0.1.0 and all failures preserved.
