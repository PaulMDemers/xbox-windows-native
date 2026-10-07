# Actual first-row kernel copy loops

The fresh trace001 diagnostic passed: 234 events, 87 paired calls, 457 resident
code pins, 24 kernel entries and 24 selected first-copy instructions. Twenty-three
rows reached the aligned forward REP MOVSD at ntoskrnl RVA60923. One 28-byte RAM
copy reached the seven-DWORD unrolled load at RVA609ec. All sampled rows returned
the original destination pointer with DF clear. No driver or configuration change.

Large rows executed with ESI equal to the captured source, EDI equal to the
destination, ECX=768 and DF=0: exactly 3072 bytes. Small main rows used ECX=64
(256 bytes). Scalar dispatch readback matched the pinned seven-DWORD jump-table
slot and actual load address. The observer removed all loop breakpoints after
the first instruction hit, then observed the paired call return. It did not
step every element or every row. No arguments/registers/return values changed.

All calls again used the direct win32k thunk into kernel memmove. No alternate
win32k MMX helper was selected. Bottom-up rectangle descriptors can still select
forward copying within each row because the two row byte ranges do not overlap.
The negative outer descriptor direction is not the CPU DF flag. No backward
kernel loop was exercised by these samples; supported observer branches for it
remain untested at runtime.

This identifies the actual CPU path; it does not attribute elapsed time between
instruction execution and framebuffer access, demonstrate GPU acceleration, or
establish hardware bandwidth. Raw paging bits and sampled surface mappings are
checked as in the preceding row trace. PAT/MTRR were not captured in this run.

After complete breakpoint teardown, Windows completed all 54 drawing cases and
162 full RGB stages, restarted normally and returned to dashboard. Cold audit
passed 324 directories, 6755 files, 325 directory clusters, zero allocation
errors/orphans, five structural hives and all protected hashes. Configuration
and pagefile mapping/content were unchanged. There was one normal shutdown and
no new warning/error/application events. Debugger diagnostic PASS is distinct
from ordinary timing qualification, which remains false for this run.

Same compiled probe107 SHA57e256841a0d39b3d850f127ac25663f0c893277bf61ffe2c4635a1f2b1a5719;
probe-provenance.json confirms identical source and executable from the previous
kit. FATX0103/HAL0102/NVNet0104/ATAPI0105/video0093, Microsoft framebuf, restored
HidServ and inherited emulator-only synthetic device policy are unchanged.
No physical access. Physical0101/video0093,0088rollback,0.1.0 preserved.

Preparation33566, runner13662, tracer6827, supervisor50201 and audit40754 are
CLOSED. Launch accepted2026-10-07T18:48:15.983566UTC. Private run disk and cleanup
records are pinned by trace001/closure.json. Never relaunch or recollect.

Review checked one-shot breakpoint ownership, entry arguments/return/stack,
actual frame pairing, ESI/EDI/ECX/DF and scalar table arithmetic, module identity,
relocated resident bytes and teardown. Independent verify-trace.py passed all
those checks plus the full cold audit and frozen-source hashes. Original byte
pins are retained in source snapshots; no unreviewed driver was compiled.
