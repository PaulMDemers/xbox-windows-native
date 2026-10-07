# Independent framebuffer diagnostic passed

candidate001 is CLOSED and fully audited. Twelve physical-framebuffer snapshots
matched1,794,048host-computed RGB pixels, covering initialization, DIB-to-primary
copies and primary overlap at64x64 and768x384. The oracle reads physical03c00000
memory directly; it does not ask the display driver for its RAM image. See
verification.json and the retained private frame-00.raw through frame-11.raw.
frame-09.png is a format conversion of its raw snapshot, also visually inspected.

Actual kernel discovery from two IDT gates agreed on823e0000. The display header
was unreadable with GDB E14 and is explicitly marked unavailable. Loader metadata,
five function prefixes and every11940bytes of relocated resident display .text
matched the pinned owned binary. Kernel and probe headers/code also matched.
There were267runtime code pins; all breakpoints were removed and the guest resumed.
The two earlier observer failures remain failed and separately preserved.

The guest then completed54drawing cases/162pixel stages and54driver selfchecks,
normal shutdown/dashboard, full allocation325directories6759files326directory
clusters with zero errors/orphans, five structural hives and all protected/payload
hashes. No new warning/error/application events. Expected display/device policy
and96MiB1536cluster pagefile remained unchanged. SharedUC acquisition matched
FCED6000→03C00000;44trace records,0drops. Cold gates and raw verification PASS.

This is a debugger diagnostic, ordinary_qualifiedFALSE. The earlier ordinary
direct/RAM matched pair independently passed its workload and cold gates. Launch
22:22:50UTC, observer completed22:24:01UTC, dashboard returned22:24:52UTC. All owned
processes are closed. Never relaunch or recollect this child.

Same0108display SHA51d98cf9ee2d2f42c360d96152877491b32773471ef8a0680d40264b49f6efc5
through all three diagnostics; no driver patch or settings change was made to
obtain this result. The explicit identity-method revision is documented in
DESIGN.md. No physical access, new mode, crash-recovery or speed qualification.
Continue with video-ram-primary/NEXT.md for broader DDI, ownership, cursor and
mode/crash gates before hardware promotion.
