# Next: coordinated framebuffer cache experiment design

trace001 is CLOSED and diagnostic PASS. Do not relaunch or recollect it. No owned
session remains. Read REPORT.md, verification.json, alias-summary.json and
source-inventory.json before new work. Full alias-scan.json and the RAM snapshot
are private retained evidence.

The next change must account for both bootvid's direct-RAM view and the desktop
aperture. Do not add P6CACHE only to the desktop mapping or edit live PTEs/MSRs.
Do not repeat a row-copy trace or treat another endpoint-only alias check as a
complete inventory.

1. Design one boot-to-shutdown policy for the whole reserved framebuffer. Identify
   when each owner creates, uses and releases its mapping, including bootvid's
   hidden backbuffer, reset/error display and late shutdown after aperture loss.
   Choose a single access model or an explicitly coordinated policy; document
   required write ordering, readback and synchronization. Keep MMIO registers UC.
2. Verify the installed NT5 mapping API's actual result and current PAT/MTRR
   state with a fresh bounded read-only diagnostic if the design depends on
   those values. Reuse the proven0094 reader rather than assuming historical
   values or substituting ReactOS videoprt behavior for Microsoft videoprt.
   Include both full mapping ranges, not just endpoints. No cache mutation in
   this diagnostic. Preserve the old0094 physical strict failure separately.
3. Before implementation, require a reviewable mapping/reservation/lifetime
   contract and a feasible recovery path. Any prototype belongs in fresh owned
   emulator children, with frozen source/binary/fixture pins and a matched
   unchanged control. Keep the20GiB build guard and resource leases.
4. Require ordinary drawing/overlap/readback, bounded repeated map/unmap and
   shutdown checks, independently observed scanout, cold integrity and unchanged
   event gates. Compare timings outside the debugger. xemu measurements cannot
   qualify hardware cache behavior or bandwidth. A physical test requires a
   separately prepared deployment and retains the working0093 rollback.

A cached shadow surface remains a separate option with explicit RAM, dirty-copy,
overlap and scanout costs. GPU acceleration and HD modes remain later projects;
none is implemented or qualified by this inventory. No speculative driver patch
or physical access is authorized by the current emulator-only investigation.
