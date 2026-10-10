# Next GPU transfer step

214 is CLOSED. Read REPORT.md, state-observations.json, evidence-review.json,
emulator-pair-review.json and both actual closures before proceeding. Never
relaunch/recollect either case. Keep the physical0101/video0093 baseline,
original0088 rollback, immutable0.1.0 and all failed evidence intact.

The snapshot gives a concrete initial state: PFIFO push/pull disabled, configured
RAMHT03000100/RAMFC00890110, channel1; PGRAPH FIFO enabled, context channel0;
retained scanout03c00000. Stable sequential samples are observations, not a
permission to reuse a channel, reset the engine or overwrite instance memory.

Start a NEW design kit by tracing the exact pinned PFIFO RAMHT/RAMFC address
interpretation, PIO/DMA submission, context switch and completion/notifier paths.
Use the actual compiled xemu source and pinned nxdk/pbkit only as references.
Specify byte ranges, alignment, width, object lookup/class/method encoding,
address translation and every ownership/lifetime transition. Do not infer
physical UMA backing from xemu's separate1MiB RAMIN model or a resource alias.
Resolve the firmware/boot framebuffer reservation conflict before choosing a
physical instance range. Do not copy pbkit's global reset or interrupt handling.

Review a single serialized NT5 context and a bounded command lifecycle: resident
source/destination/command/completion storage, sequence identity, interrupt or
bounded completion observation, drain, timeout quarantine and crash/display
handoff. A successful CPU allocation from213 is only a precursor. Address
translation, RAMIN access and completion must each have explicit contracts.
Do not reuse timed-out allocations or report successful completion on timeout.

Then validate the exact arithmetic/command planner and lifetime state machine
with independent host oracles and fault cases. Only a concrete reviewed protocol
can justify a fresh emulator child for one disjoint guarded16x8 transfer; keep
scanout, modes, cache attributes and physical devices unchanged. Compare exact
source/destination guards and pixels before/after, preserve runtime source and
binary pins, normal shutdown, complete cold audits and unchanged event gates.
Register equality or zero interrupt words cannot substitute for completion.

Use new IDs, frozen inputs and cooperative leases; inspect capacity before a
build. C had22101704704 bytes free during214, only slightly above the unchanged
20GiB guard. No casual backing-chain moves. No physical deployment or other
device-thread integration follows from214. Timing/performance claims require a
later matched benchmark; whole-boot Ftdisk49 remains a strict failure.
