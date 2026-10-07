# Review of file-specific paging diagnostics

Candidate0101 bytes/hash and compiler-derived offsets are pinned. Live kernel
header/timestamp/module list establish the driver base; reviewed relocation
operands and instruction bytes are checked before arming. VfatWrite takes a
pointer to a context pointer. Unicode paths are length-bounded and decoded.
Only the actual SetupAPI.log file's buffer records are retained.

The added site is exactly after VfatGetUserBuffer returns and before its EAX
result is stored. Reviewed frame instructions establish clipped Length at-124,
resolved ByteOffset at-96 and IrpContext at-100. The debugger does not ask Windows
to map pages or modify arguments. Captures are capped at64KiB and hashed; unread
entry MDLs remain explicit. Return pairing uses thread/stack/return address and
context, without treating STATUS_PENDING as completed I/O. Source bytes are
compared with corresponding exact cold offsets after owned cleanup.

The first attempt preserves its20,000-hit source; the second removes cache-call
traps and extends the bound. This addresses a coverage gap only. No full-page
writeback timing hypothesis is promoted to fact until observed. Atomic snapshot
replacement and a supervisor wait keep tracer cleanup ahead of runner teardown.
No filesystem driver source, installed console or immutable fixture is changed.
