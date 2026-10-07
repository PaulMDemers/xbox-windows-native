# Bounded kernel memmove loop observation

Fresh trace001 child with unchanged compiled probe107, drivers, settings and
inherited emulator device policy. Emulator only. Previous row-copy trace is
closed and will not be relaunched or recollected. Preserve physical baseline.

Extend the paired first-row trace with one actual kernel memmove entry stop
and one actual first bulk-copy instruction stop per row. Pin code, require
the exact row arguments and return address at entry, and capture EFLAGS plus
ESI/EDI/ECX at the selected REP MOVSD or scalar unrolled load. Remove all loop
breakpoints after the first hit; no per-element stepping or guest mutation.

Scope is DWORD-aligned first rows whose byte lengths are multiples of four,
as seen in the preceding trace. Fail explicitly if this condition changes.
Support forward and overlapping backward paths, REP and short scalar paths.
Pin the selected scalar jump-table slot and require its target to match the
executed load. Source/destination row bounds and page mapping checks remain.

512 outer stops/600 seconds; same thread/frame pairing and complete finally
teardown/resume. Timing under debugger is unqualified. After normal restart
require all 54 cases/162 RGB stages, full cold allocation, five structural
hives, protected hashes, unchanged configuration/pagefile and strict events.
No cache/renderer patch. Raw PCD/PWT alone does not establish PAT/MTRR policy.
