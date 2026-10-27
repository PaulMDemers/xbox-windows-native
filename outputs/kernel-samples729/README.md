# Kernel blank/gate/sequencer samples729

Fresh probe based on authored728 source, whose physical runtime is closed.
Register data writes and CPU admission are unchanged. It adds32 full630/CR1b
pairs after restoring630 while gate=5 andSEQ1=21; then a full pair andSEQ1
read aftergate4, before restoringSEQ1. The original direct/indexed reads and
32 late pairs remain. Extra observations alter timing; no causal claim follows
merely from the first changed sample being after a particular write.

All125 raw words are saved after original flags are restored. No paging/cache
changes or kernel APIs inside the boundedCLI interval. The first54 words keep
the728 layout. See schema001.json for appended arrays/counters. Full baseline85
restoration is still required; no repair, mask or pending-bit clearing.

Green top bar means729/full baseline and selectors passed; orange7295/7298;
red another refusal/failure; magenta a post-probe persistence failure. Intended
display15seconds followed by automatic firmware return, not Windows shutdown.
Seven exclusive E reports, flushed/read back, no startup hook or C access.

Build under the existing build lease with build.py; run model.py and
layout_model.py under the emulator lease. Run the three linked-byte review
scripts and review_prepare.py before physical.py stage. One fresh20secondSITE
request only after watch/reset readiness; never retry accepted/uncertain launch.
Collect once after dashboard return and audit all source/stage/result pins.

The compiled model tests39 cases: transitions on630, during blank samples,
atgate, atSEQ, later or never; unlock read03/57; CPU/initial-state refusals;
dropped writes and restoration failures.2353 layout cases and instruction-byte
checks complement source review. These models do not prove hardware semantics.
