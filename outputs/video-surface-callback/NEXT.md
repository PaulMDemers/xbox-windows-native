# Next: establish the watched surface's lifetime and synchronization needs

Read REPORT.md, surface-verification.json, trace-verification.json,
recorded-surface-tests.json and lifecycle-followup.json. This candidate is CLOSED and diagnostic/cold PASS.
Never relaunch or recollect this candidate or either earlier address diagnostic.

Three identical-size guest uploads use the same local memmove/rep movsd and
recorded paging flags. The selected lower upload has 17,280 write callbacks against
surface 0x03c64000, one at every four-byte destination address for rows 160..249.
The two top uploads and selected shadow-source reads have none. The earlier
ordinary position benchmark remains separate from this debugger diagnostic.

This establishes position-dependent callback overlap, not measured callback
duration, dirty-download waiting, full causality, or a physical Xbox speed fix.
The surface's exact creation/size/lifetime was not captured; do not call it stale
or attribute it to the dashboard without additional evidence.

Next NEW owned child should enable only sparse existing surface create_color,
create_zeta, invalidated, evict_reason, upload and download lifecycle events from
emulator startup, with bounded file/record volume. Pin the generated backend and
actual binary. Record prelaunch and marker offsets; keep CPU-access events gated
to the same three draws. This can identify when 0x03c64000 appeared, its geometry,
whether it survives the Windows handoff and whether CPU access downloads GPU data.
Capture relevant guest reset/handoff writes only if lifecycle evidence warrants.

Do not blindly remove callbacks, flush renderer surfaces or change guest caching.
Any fix must retain CPU/GPU data coherence and validate normal GPU reuse as well
as the CPU-rendered desktop. A generic callback optimization needs correctness
tests for dirty GPU downloads, subsequent CPU writes and later GPU consumption;
a handoff/reset fix needs evidence of the actual hardware contract.

Hardware unchanged: physical 0101/video0093, 0088 rollback, immutable 0.1.0 preserved.
Keep the 20 GiB guard and existing backing chains. Ordinary RAM0112 benchmarks and
debugger/cold integrity results are separate; no physical performance claims.
