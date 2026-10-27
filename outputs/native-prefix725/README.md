#725 staged: CR1b readings through native cleanup

No725 launch yet. Closed724 passed all forward writes/readbacks, then returned
cleanup failure7245 withCR1b85 instead of05. The exact transition is unresolved.
This new diagnostic preserves724's forward/cleanup data writes and adds four
bounded, selector-preserving CR1b reads. Existing immediate/final values are
copied, giving six samples. It still stops beforeCR22 and does not program
encoder/timings, retryCR1b, restore85, clear pending bits or relax a check.

## Report

13 rows,32 bits MSB left; white1,black0 on gray. Rows0..5 are signature7250000d,
bridge phase, admission stage, return code, MMIO count, CRTC count. Rows6..11:

1. Existing immediate read afterCR1b05.
2. AfterCR19 restoration.
3. After680630 restoration.
4. After output gate4.
5. AfterSEQ1 restoration and its readback.
6. Existing finalCR1b cleanup read.

Row12 is cleanup_ok. Unreached samples areffffffff. Expected clean result:
7250000d,4,5,725,11,4,5,5,5,5,5,5,1.
Orange7255 with later85 is a cleanup failure, not a pass. Other cleanup fields
are not exported. Added reads change timing; a first85 sample brackets where
it was observed, without proving register semantics or an operation's causality.

## Validation and provenance

Fresh payload001, host002, twelve disklessCPU fixtures (all closed),59 native
integration cases including five independent transition vectors,76 whole-frame
optical cases,30 nxdk page cases,372 nxdk ownership cases and131379 host
ownership cases passed. Source comparison confirms original noninstrumentation
prefix tokens/data-write sequence and frontend geometry unchanged. Linked
object nonrelocation instructions and embedded payload/bridge match PE andXBE.
Result296bytes;17 relocations (11absolute/6PCrelative), padded payload9916bytes.

Preserve host001 failure: the old parser required16 total relocations and
rejected the new17-entry ELF before building pages/CPU fixtures. Fresh
relocate002/host_build002 retain bounds/type/overlap checks and require17.
No console run occurred during that failure. Closed724 failures stay preserved.

Active sources: main.c, probe.c, transaction725.c; host_build002.py (host002),
cpu002.py, integration002.py, optical_review002.py, build002.py (build001),
page_review002.py, plan_review002.py, linked_review002.py, physical.py.
sources001 freezes all source bytes; review001 pins successful checks.
No closed runtime was reopened; retained sources only were reused.

## Staging

Owned /E/Applications/XWNMode725/{owner.json,default.xbe} only. Readback matches
XBE SHA256 cba54312e5d70f7ff330644128eabab6823481fe937dc442239474c13284eef2.
No startup hook, dashboardC access, ordinary launcher or Windows changes.
Console is at UnleashX; watcher/reset readiness pending. Deliberate held picture
needs a photo before power cycle, then a single collection. No725 launch yet.
No native full-mode/Windows or acceleration qualification.
