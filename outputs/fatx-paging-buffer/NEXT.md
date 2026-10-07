# Next: controlled interruption between the two observed page writes

Use a NEW owned emulator attempt and fresh overlay of the same immutable draw001
input. Keep physical0101/video0093, release0.1.0 and all completed evidence intact.
The completed paging002 normal shutdown is a control, not a physical result.

Make a narrowly scoped guest-stop diagnostic that observes the exact log suffix
write at270336,109 effective bytes and its successful VfatWrite return. Before
interrupting, require the target prefix page has not been observed written.
Freeze guest execution at that checkpoint, preserve the trace and any necessary
owned RAM evidence, remove debug breakpoints while stopped, and exit only that
owned emulator without allowing a Windows shutdown. This models loss of guest
volatile state; host emulator exit/cache behavior differs from physical power
loss. Do not silently label it an ordinary restart or a successful stability run.

After verified emulator exit, cold-read the exact220-byte range and compare it
with immutable-before zeros and the normal002 output. Check whether the suffix
persists while the111-byte prefix remains old. Inspect allocation/hives as
interrupted-state evidence rather than waiving normal-shutdown/event gates.
Retain every partial/failing stage. Do not use the standard supervisor's normal
return requirement as an expected-success gate for an intentional interrupted run.

A matching split result would establish a mechanism in this emulator fixture,
not the original hardware cause. If disproven, preserve it and trace lower disk
submission or the actual mapped-append API lifecycle. Static SetupAPI candidate
routines77893f87/77893da6/77893cb5 appear to copy into a mapping, seek, unmap,
close mapping, SetEndOfFile and close file; their use by this logger still needs
runtime confirmation. Earlier mapped-eof tests primarily read mappings and
WriteFile outputs. A normal writable-map/extend/unmap/truncate regression may
supply missing coverage, after the lifecycle is established.

Before starting, check time. User cutoff13:00UTC7October2026. At cutoff perform
cleanup/report and pause xbox-emulator-development-until-10am. No physical FTP.
