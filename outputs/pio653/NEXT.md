# After653: resolve the transport boundary before more implementation

Read REPORT.md, host001.json and compiled001.json.653 is a completed diskless
prototype, not a hardware candidate. Do not rerun these attempts, reuse651 as a
runtime, or set permit_status_ack in a native caller to bypass review.

The next bounded source task is to decide where a captured display result can be
exported without changing the display experiment. Trace the pinned651 success
and failure paths through BootResetAction and the existing IDE initialization.
Keep capture-before-display, capture-after-result, and subsequent transport
effects distinct. Assess whether a deferred export after the existing normal
storage initialization can cover successful boots; record explicitly that it
would not by itself cover the current early-reset failure path. Do not move the
initialization, change failure cleanup, or silently clear pending bits.

If a practical route cannot capture both outcomes within those constraints,
document that limit and choose a smaller diagnostic strategy. Do not expand a
general storage subsystem or repeat physical boots solely for more LED ambiguity.
The existing source may be read; closed runtimes may not be reopened/recollected.

If native PIO remains justified later, it requires all of the following before
staging: verified native register/PCI bindings and controller ownership; a finite
settle implementation with its minimum delay proven; an explicit accounting of
interrupt side effects that respects the experiment; live FATX allocation and
non-overlap proof for a unique owned file; private identity/fresh seed readback;
caller and RAM/stack validation; fresh compiled failure tests of the integrated
binding. Geometry alone is insufficient and no physical addresses may be guessed.

Only a newly frozen candidate with those facts can enter the ordinary one-SITE,
bounded observation/cleanup/audit workflow. Nothing is staged or queued now.
Preserve protected720p, ordinary startup, private recovery and prior failures.
Console last observed dashboard after651; physical lease retained, automation
paused, no hook/rollback/process outstanding. No hardware input needed now.
