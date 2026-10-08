# Crash visible and cold header correct; diagnostic remains failed

crash001 CLOSED, never relaunch/recollect. The corrected fixed-image entry pin
worked and two IDT gates identified actual kernel823e0000. At KeBugCheckEx,
reading RAM0109's first text page failed GDB E14. Observer removed all breakpoints
and resumed; its requested complete-display-text residency gate did not pass.

A separately recorded read-only physical snapshot after observer failure checked
18 actual process page directories. Every one shares the same PDE for this
mapping and lacks a present PTE for the first display text page. This is not
merely a probe-process mapping difference. Drawing-code pages and ownership
data are mapped. No demand fault, page-in, register edit or driver change was
introduced to force the failed condition to pass. The post-failure snapshot
cannot stand in for missing before-crash evidence.

Supervisor allowed90 seconds following failure. Captured screen visibly shows
the intended E058D103 cookie and dump-complete text. Cold PAGE DUMP/cookie is at
the intended high-LBA offset; former alias unchanged with no writes. Full
allocation326dirs/6761files/327directory clusters has0errors/orphans. Five hives,
35protected files, staged payload/startup hashes, unchanged configuration/pagefile
and strict event deltas pass. Runtime dump return and exact payload pairing are
unobserved, so dump_write_evidence_passed remainsFALSE.

The next diagnostic should measure actual mapped display pages and ownership,
while requiring the complete crash-rendering bootvid text and genuine dump return.
This deliberately does not claim whole RAM-driver residency: inactive display
code need not execute during boot-video takeover. Preserve this failed full-text
residency attempt and all its evidence; no physical qualification or recovery.
