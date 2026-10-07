# Paging input captured; target coverage is partial

Case001 launched05:47:55UTC7October2026 and completed a normal restart. The
tracer stopped at20,000 hits before shutdown, removed all breakpoints and resumed
Windows with no pending target records. Cold checks passed.

All52 captured post-VfatGetUserBuffer ranges exactly match the final cold file.
Twelve target-overlapping ranges contain the109-byte suffix at270336 and all
returned success with the exact effective byte count. The111-byte prefix at
270225 was not captured: the last observed earlier-page write ended exactly at
270225. The complete220-byte warning is nevertheless intact in the cold file.
Full target coverage remains FALSE. No source mismatch/corruption was reproduced.

A later full-page writeback outside the bounded trace is a hypothesis, not yet
an observation. Case002 removes the unrelated cache-call breakpoints and raises
the bound to observe through dashboard return. It retains the same unchanged
guest input. Case001 source remains immutable in trace-source.py. No repeated
launch or collection, no driver changes, no physical-console access.
