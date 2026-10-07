# Next discriminator

trace001 is CLOSED and fully audited; never relaunch/recollect. All owned
sessions are closed. Read REPORT.md and trace-verification.json. No physical
access, driver change or hardware performance qualification occurred.

The measured ordinary delay is inside BitBlt, and the sampled row calls now
resolve to kernel memmove, with framebuffer-aperture mappings. Next use a NEW
bounded child to observe the actual first-row memmove entry and selected copy
loop, retaining paired return, resident pins and full teardown/cold audit.
Static leads in the pinned ntoskrnl are RVA608f0 entry, RVA60923 aligned forward
REP MOVSD, RVA60980 after alignment prefix, and RVA60a88 overlap/backward entry.
These are static leads only: verify control flow and exact bytes before arming.
Do not linearly decode jump tables as code or claim an executed REP path yet.

Capture actual ESI/EDI/ECX and direction at the selected loop once per first
row; avoid per-iteration stops. Include any alternate small-copy/overlap branch
needed to explain each sampled call. Keep the unchanged probe/driver stack and
fresh IDs/guards. Separately inspect PAT/MTRR and alias policy through a reviewed
read-only mechanism if needed; raw PCD/PWT alone is insufficient to change it.
Only then choose a bounded renderer or access experiment with exact pixels,
ordinary matched timing and lifecycle/scanout gates. No speculative cache patch.

Preserve the original physical 111-byte corruption as unresolved and all failed
cases. Old automation stays paused; current user authorization is emulator-only.
