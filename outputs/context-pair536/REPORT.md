#536 warm/cold instrumented comparison: warm case collected

Warm case1 reached the Windows desktop after534 Windows Restart without an
intervening power cycle. User then reported dashboard return after our normal
Windows Restart request. Actual after1 collection completed19:28:27UTC,
October18,2026 (supervisor closed19:28:28UTC). All five hives passed raw and
independent parser checks; ordinary launcher/startup and720p baseline are exact.
System event delta includes one6005, one6006, oneFtdisk49 and three Application
Popup26 records (rundll32 window station shutting down). This confirms a normal
shutdown record, not an error-free event log or complete filesystem health audit.

Primary, handoff and context receipts are present and decode without errors;
no refusal record. Preparation and loader/payload byte checks passed. Both CPU
snapshots agree on CR0/2/3/4, selectors and descriptor-table registers. They are
before/after witness IO, before the context packet's own IO and final handoff;
no pagewalk, descriptor contents, own-close or final-transition proof is claimed.
Actual Windows execution is supported separately by user and event evidence.

The first collection supervisor failed the unchanged capacity gate before
creating capture files or doing network IO. It remains preserved. User authorized
old-build cleanup;538 removed six obsolete negative-test fixture copies, freeing
6.2GB. A new after1-only supervisor002 collected this still-uncollected run using
the unchanged frozen controller. No console launch was retried.

Cold case2 is staged but NOT launched. User has been asked to power off at
UnleashX for about10seconds/on and report ready; await that answer. Then save
ready2, supervise before2 and launch2 once. On desktop request normal Restart;
collect after2, audit2 and decode2, compare actual evidence. No third launch.
No startup hook, ordinary driver/launcher patch or dashboardC access.

This warm instrumented boot succeeded, so it does not reproduce ordinary532's
warm failure. Added recorder code/layout/IO/timing prevents treating it as a
fix or conclusive test of the ordinary launcher. Preserve warm532 success/fail/
success and cold534 success/success. No GPU/game/release promotion.

Preparation: both images exactly reconstruct494/490 except four fixed-width
receipt paths and section digest.29 modeled admission/launch/receipt checks and
six modeled stage/capture checks passed; full pins and readback were verified.
Read DESIGN.md and NEXT.md with this current report; their frozen preparation
instructions predate the preserved capacity-refusal/new-supervisor recovery.
