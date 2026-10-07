# Next questions after controlled interruption

The normal control is `../fatx-paging-buffer/002`. Case001 raw bytes split111/109
but the persisted file is too short to expose the target; allocation also fails.
Case002 failed at host atomic trace replacement; all failed evidence and the
resumed guest's clean cold file are preserved. Case003 uses the tested recorder
and stops at the later1524-byte write: file size271385 exposes111 zeros followed
by109 correct bytes. Allocation is consistent but normal shutdown was prevented.
All three cases are CLOSED and audited. Do not relaunch or recollect them.

Next prioritize runtime identification of the
actual application's mapped-append lifecycle. Static owned setupapi.dll review
still does not prove the candidate functions below are used for this log.
Preserve a zero-hit result if they are not. Do not patch FATX based on a candidate
function name inferred from disassembly.

Pinned setupapi.dll SHA256:
`1d0a6e9d062a51e71eaae93d776746823834f5c518096d340f2b332fc059a23d`.
Owned original path is in the0.1.0 private physical-files archive. Candidate
outer routine77893f87 has a wide path and two ANSI strings, plus a fourth flag.
It calls helper77893da6, which opens the file, reads old size, creates a writable
mapping grown by an extra amount, then maps it. Candidate caller copies strings
and punctuation into that view, seeks to the new size and calls cleanup77893cb5.

Useful static boundaries, all require exact pinned-byte and runtime verification:

| Site | Address | Observation |
|---|---|---|
| Outer entry |77893f87|ESP+4 path; +8/+12 strings; +16 flag|
| Mapping helper return |77894020|EAX status; caller locals populated|
| CreateFileMappingW call |77893e69|Six arguments atESP|
| MapViewOfFile return |77893e85|EAX view, old sizeEDI|
| SetFilePointer call |778940e2|File, new offset, high pointer, origin atESP|
| Seek return |778940e8|EAX offset; mapped view EBP-0x3c; oldsize EBP-0x54|
| Cleanup call |77894121|View,file,mapping,unused,truncate flag atESP|
| UnmapViewOfFile call/return |77893ce8/77893cee|View atESP; EAX BOOL after|
| Mapping CloseHandle call/return |77893d05/77893d0b|Handle atESP; EAX BOOL after|
| SetEndOfFile call/return |77893d28/77893d2e|File atESP; EAX BOOL after|
| File CloseHandle call/return |77893d50/77893d56|File atESP; EAX BOOL after|

Keep process/thread/stack pairing. Capture complete target source bytes before
unmapping and distinguish them from later kernel paging buffers and cold data.
No flush was found in this statically examined cleanup path; that alone is not
proof of an application bug, a missing required flush, or its use for SetupAPI.log.

Pinned0101 source cleanup updates dirty directory entries, then calls
CcUninitializeCacheMap(FileObject,&FileSize,NULL); UpdateFileSize calls
CcSetFileSizes. These are leads for explaining observed ordering, not evidence
that the APIs are wrong or should be patched. First confirm actual caller.

A focused writable-map/extend/copy/unmap/truncate regression with normal shutdown
would complement earlier mapped-read/WriteFile tests, once the lifecycle is
verified. An intentional interruption is never a normal persistence PASS.
Physical original reboot method remains unknown. Keep all physical access off
and enforce13:00UTC7October cutoff and existing resource leases.

The physical damaged prefix contained non-ASCII data; the emulator input's
corresponding raw range is zero. A file-visible zero-prefix split would match
the boundary and incomplete persistence, not the original damaged bytes. Do
not equate those observations or prefill the target just to manufacture a match.
