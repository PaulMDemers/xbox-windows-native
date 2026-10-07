# Resume point

The cache-primitive review is complete. No guest, physical test or driver build
was started. Read REPORT.md, DESIGN.md, SHADOW-PLAN.md, inventory.json,
replay.json and shadow-contract.json. Existing shared UC0106 remains unchanged.

Do not implement a late fixed-buffer UC/WC remap: actual reserved mapping rejects
live replacement, and unmap/remap leaves a nonpresent-PTE gap for crash drawing.
Fifteen isolated instruction cases passed as analysis, not guest qualification.
Seventeen resident function windows checked: sixteen PE matches plus the explicit
KeFlushCurrentTb CR4.PGE variant. The nonexported INIT helper was disk-only.
Historical cache/TLB helper labels were corrected in new evidence; preserve old
source/JSON and the initial inspection failure. No actual WC transition occurred.

Next create a fresh display prototype kit. First build and qualify a renamed
direct-framebuffer DDI from the pinned ReactOS source lead against existing
Microsoft framebuf, with explicit NT5 imports, cleanup and capability review.
Only then add the private RAM bitmap/opaque surface and complete upload coverage.
32 required owned NT5 engine exports exist; no replacement display DLL is built
or qualified yet. Existing54/162 checks need independent scanout and extra DDI
coverage for a shadow candidate. Performance is unproven.

All owned sessions remain CLOSED; no emulator process. Do not relaunch/recollect
old shared-trace001/002, shared-crash001 or other closed attempts. Crash001 disk
remains preserved, never booted. Physical0101/video0093,0088rollback,immutable0.1.0
and completed128GiB recovery remain intact. Original111 non-ASCII corruption and
unknown first restart are unresolved. Emulator ONLY; no physical FTP/deploy/test.
Old automation remains PAUSED. Recheck actual C: capacity;20GiB guard unchanged.
