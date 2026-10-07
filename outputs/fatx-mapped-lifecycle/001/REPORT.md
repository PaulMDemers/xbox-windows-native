# Initial lifecycle trace: unreadable memory, no source coverage

The actual installer launched06:32:40UTC7October2026. The tracer stopped with
GDB E14 at06:33:05 before recording its first verified hit. The failed read's
address was not retained, so this result does not establish whether instruction
bytes or the pageable PE header were unavailable. No source calls were captured.

All breakpoints were removed and the guest resumed. Normal dashboard return and
cold collection followed; the complete warning, allocation, five hives, selected
binaries, installation, event and normal-shutdown checks passed. This does not
repair the missing runtime coverage. Exact trace/site/review sources are saved
under001 before any instrumentation correction.

Case002 uses a fresh overlay, records the last stop and precise memory read,
and checks up to32 pinned resident code bytes at each candidate boundary. It
does not depend on reading a pageable PE header. Unreadable code hits are
explicitly counted, skipped without collecting evidence and bounded at100;
readable mismatches remain fatal. Before/after cold DLL hashes independently
verify the exact SetupAPI binary. No driver or guest-memory change is involved.
