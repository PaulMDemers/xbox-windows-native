# PC606: failed park trace identifies an output-pointer assumption

The instrumented game reached Forest Frontiers and moved the camera, but the
recorder terminated it while opening the Load dialog. No park-phase transition,
saved-park capture or cost measurement occurred. This attempt remains failed.
Windows then restarted normally; registry restoration, unchanged save, copied
tools, protected OS bytes and cold hive checks passed.

The last fully paired call406 was CreateDIBSection from a caller inside GDI32
at0x77f44b9c. It supplied NULL for ppvBits and returned bitmap0x050501d2. The frozen
recorder logs RETURN, then rejects that NULL output address in outputs601 before
emitting OUTPUT. This deterministically makes ownedbreak fail and triggers the
debugger's child termination. The recorded access violation follows TERMINATE,
so it is not evidence of the initiating game failure. Stale GetLastError121 does
not identify the guard, and no event/time-bound failure should be inferred.

The header was128x288x16 BI_BITFIELDS. The bounded reader explicitly returned
unsupported compression status8 without making the call fail; it did not read
the masks. The fatal condition was the separate output-pointer guard.
[Microsoft's API documentation](https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-createdibsection)
describes ppvBits as an output pointer but does not explicitly promise NULL
acceptance. The observed internal NT5 call returned a nonzero handle with NULL;
qualify a new original control instead of generalizing that behavior to all
Windows versions or weakening unrelated output/read checks.

## Partial evidence, kept separate from the failed objective

The cached trace has406 correctly paired calls and36 independently decoded
header observations. RCT's one successful DIB creation and32 early StretchDIBits
samples share the same bits pointer and header:

| Field | Early RCT observation |
| --- | --- |
| Width / signed height |1024 / -768, top-down |
| Pixel format |8 bits per pixel, one plane, BI_RGB |
| Row stride / derived extent |1024 bytes /786432 bytes |
| Declared colors used |256 |
| Sampled StretchDIBits return |768 |

These are early samples from a failed debugger run, not loaded-park observations,
frame counts, palette contents, pixel allocation accessibility, costs or Xbox
acceleration. Seven private captures show title/scenarios, Forest Frontiers,
Window mode, camera movement and the Load menu. The requested saved file was
290244 bytes; the runner found no Load dialog after the recorder terminated the
game. No phase request was sent.1999 capped StretchDIBits entries were skipped
before termination.

## Preservation and cleanup

Source review001 rejected a CRLF-to-LF difference in the inherited IAT header.
Review002 verifies exactly that normalization; addresses/tokens and runtime code
were unchanged. The first display keep-settings timer expired; the second attempt
confirmed1024x768 HighColor16 before the sole game launch. Both failures remain.
Build001 compiled; native NT5 imports, frozen source and503-file media/guest-copy
verification passed. An inherited preparation console label says603/uninstrumented;
the606 paths, sources, manifests and debugger handoff identify the actual run.

Review001 is preserved failed at input_sequence_submitted. failure-review001
inspects the raw failed trace without fabricating a successful END or phase.
All406 returns pair correctly, but the trace's actual terminal status is97/failed1.
The runner reports debugger exit1. Registry restoration and one new6006 passed;
the VM exited2026-10-20 04:44:31UTC. The cold audit enumerated7003 files/315
directories; five hives were clean with raw-value agreement. Only expected
CSS0.DAT/Game.cfg changes occurred among game assets; the exact PC593 save was
unchanged. Raw event timestamps agree with normal restart. The inherited DRM
typed-decode limitation and incomplete NTFS allocation-audit coverage remain.

All owned VM/build/cold processes exited.606 is CLOSED; never reopen/recollect/
parent it. Xbox untouched, last dashboard/no owned hook;596 SOFTWARE cleanup is
still cold-only. Launcher/protected720p/transfer ZIPs and accepted manual save/load
are unchanged; ZIPs exclude RCT. No game or driver fix is claimed.
