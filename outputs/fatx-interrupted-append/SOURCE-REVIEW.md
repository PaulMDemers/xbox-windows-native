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

The interrupted experiments reuse these reviewed sites. Case001 stops after
the109-byte suffix write completes;002 stops after a later1524-byte write at the
same offset, still requiring the exact109-byte source suffix. Both reject any
previously observed write overlapping the target111-byte prefix or any pending
target log write. The guest remains at the return breakpoint during breakpoint
removal, monitor paused-state confirmation and HMP quit. There is no resume or
single-step after the accepted checkpoint. Exact001 source is preserved.

The HMP quit socket may reset rather than return a monitor prompt; case001
records that exception without erasing it. Separate owned process exit evidence
is required before classifying it as an exit disconnect. This is distinct from
a failed breakpoint removal, missing paused state or unsuccessful guest resume.
No filesystem driver source, installed console or immutable fixture is changed.
