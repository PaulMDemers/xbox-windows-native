# PC609: Load dialog passed; tracked DLL unload stopped the recorder

The corrected package copied and verified503 assets, then the single game run
reached Deluxe's title, Forest Frontiers and Window mode. Its camera moved.
The Load Game dialog was found uniquely, accepted the exact PC593 save path,
received one Open submission and disappeared. The runner then could not reacquire
the game: the recorder had deliberately terminated it at a tracked DLL unload.
No loaded/stable park capture, reference match or second phase was obtained.

The607 absent-output fix worked in actual RCT execution: calls406,407 and461
returned nonzero bitmaps with absent ppvBits, and all three OUTPUT_ABSENT records
were retained. This advances beyond606's first failure. It does not convert the
overall run to a pass.

## Exact stopping condition

The trace contains536 paired calls/returns,47 headers and163 breakpoint sites.
All recorded calls returned. Immediately before TERMINATE it reports
UNLOAD_TRACKED for base0x71500000, site129, address0x7157e4de. Source unload601
rejects any recorded breakpoint in an unloading module without consulting armed,
enabled or reference state. The first module contains15 recorded return sites and
no pending return calls in the trace. That is reconstruction from paired records,
not a live dump of debugger flags. A second marker for0x03e00000/14 return sites
appears after requested termination and is not the initiating event.

END is97/failed1, with536 requests and returns. No PHASE was requested;
2046 capped StretchDIBits entries were skipped before the park phase. Stale
GetLastError121 does not identify the failed condition. This is a recorder lifetime
limitation; the trace does not establish a save failure or spontaneous game crash.
Seven private captures were visually inspected. Their camera comparison confirms
movement, but no reload comparison is possible. No FPS, costs or Xbox acceleration
result is claimed.

## Validation and cleanup

Build, native NT5 imports and exact607 helper inheritance passed. The new copy
contract checks ordered tool names, source/destination equality, manifest hashes,
failure guards and verifier placement. It rejects608's actual bad batch plus nine
mutations. Scene comparison controls pass seven rejection cases. The full game
review001 remains failed at input_sequence_submitted; the independent failure
review checks actual failed records without fabricating a successful END.
The full positive game trace mutation suite was not run because its prerequisite
failed. Unused success close001 is retained; close002 records the actual failure.

Normal Windows restart ended the VM at2026-10-20 05:36:40UTC, exit0, with no host
force. The final automatic screenshot raced process exit and logged
FileNotFoundError with process_exit0; preserve that error. Cold audit enumerated
7003 files/315 directories, checked exact tools/OS/seed,503 assets with only expected
CSS0.DAT/Game.cfg changes, byte-identical PC593 save, restored registry, five clean
hives/raw agreement and one new6006. Corrected event-timestamp checker002 removes
inherited fixed record-number prose; actual chronology passes. The original is
preserved. DRM typed-decode and incomplete allocation-audit limits remain.

All owned processes exited.609 is CLOSED FAILED; never reopen/recollect/parent it.
The next experiment is an original DLL unload/reload lifetime control before a
new game run. Xbox untouched, last dashboard/no hook;596 cleanup is cold-only.
Launcher, protected720p, saves and transfer ZIPs remain unchanged; ZIPs exclude RCT.
