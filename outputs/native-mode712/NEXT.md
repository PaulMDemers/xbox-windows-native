#712 CLOSED: watched BLACK then restored picture/GREEN hold

Read observation001/002, collection001, audit001 and closure001. User separately
confirmed both the final green hold and black-then-return sequence. After a
confirmed manual power-cycle, nine reports were double-read and audited once.
PCI/CRTC/SEQ/geometry/allocation mappings equal711; all pins and independent
alias checks pass. Last persisted phase handoff_armed is preparation only.
Console at dashboard; no startup hook or owned process. Do not rerun/recollect712.

Next NEW713: isolate704's phase3 extended-register unlock immediately after
blanking: CR1f write57 and check that CR11 matches its captured baseline. Preserve
all712 baseline, bounded restoration and diagnostic result obligations. Never
write CR11, clear pending bits, or add common PRAMDAC/CRTC setup, geometry,
encoder or clock programming to this first boundary check. Restore visibility
once on ordinary failure, without kernel calls/retries; report actual failure
code/readbacks distinctly if needed. Do not try to restore CR1f by writing its
readback: the key/read semantics are not interchangeable. Hold for manual reset.

Review pinned primary-source handling and validate exact linked/relocated
instructions, selector save/restore, CR11-change rejection, return codes, bounded
blank restoration, allowed writes, allocation/stack and optical guards on fresh
host fixtures before staging. A successful unlock-key request plus unchanged
CR11 does NOT prove extended writes are unlocked; later changed-register
readback must establish that. No functional fix or native-mode promotion.

712 establishes one observed blank/restore pair, not each gate independently or
the cause of708/709 failure. Preserve those failures and possible intermittency.
708/709/710/711/712 are CLOSED. Hardware ticket retained, build/xemu released,
automation paused. Original720p/ordinary launcher protected; console C off limits;
other work tabled. No additional reset is currently needed.
