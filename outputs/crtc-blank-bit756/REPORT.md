# Test756: second CR05 horizontal blank-end bit, prepared

Source-only extension of kernel754 after native755 passed CR03. This adds the
next pinned legacy write: CR05 bits0..6 retained, bit7 replaced from horizontal
blank-end. Expected CR05 sequence31->3e->be->3e->31. It distinguishes first write,
second write, intermediate undo and final own-byte restoration. CR00/02/03/04
neighbors are checked after the second write. Any intermediate undo mismatch
inhibits output even if final full-byte restoration succeeds.

152 compiled COFF cases pass, including14 new write/read/neighbor/undo faults;
2353 layout cases pass. Actual clock gate passes10 cases after correcting the
host harness stack-local bounds; original failed clock-model001 preserved.
Exact linked instruction bytes, independent source delta and153-word schema
mutation checks pass. No native handoff/full-mode/Windows evidence implied.

Unique E stage/readback passed. No startup hook or launch yet. No owned VM or
host process. Kernel automatic return is authorized. Console authenticated at
UnleashX during stage. Sources frozen before stage; new kit attributes set.
