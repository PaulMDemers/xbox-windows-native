# PC622 closed failed qualification: subject outlived measurement

All eight original timer cases completed and Windows restarted normally.
Runtime20:43:58.920853Z to20:48:45.783625Z2026-10-20; no game/physicalXbox.
Cold audit passed6495 files/310 directories, five clean hives, exact tools/OS/seed
and one normal shutdown. Seven suspension,23 snapshot/timer and five serial
negative cases passed before launch. No workload/build/UI failure occurred.

The actual review failed its unchanged call-count boundary gate in observed
busy timeGetTime case4. Its20s CPU window ended at208171ms; the subject kept
polling until209734ms while224 samples were flushed.1.563s exceeds the declared
1s ending allowance. Preserve review001's failure and raw logs; no timing-bound
waiver, repeated launch or closed-disk reopening. Earlier unobserved cases passed
the oracle but do not qualify the failed combined comparison.

623 is a new immutable404 child with the release/join block moved after end
counter/module capture and before buffered log writes. Workload and sampling
loop remain exact apart from namespace; acceptance limits unchanged. No functional
game/driver change, FPS or Xbox acceleration claim. Original console last known
dashboard/no hook;596 SOFTWARE cold-only; automation paused.
