# Paired calls and returns: original NT5 control

This extends the qualified597 entry recorder in a new owned process. It reads
the target's actual IAT, captures entry stack arguments, sets a breakpoint at
the observed return address, and records EAX only when the same thread's top
frame returns to that address with the expected stack pointer. LoadLibraryA and
GetProcAddress use their stdcall cleanup; the original probe uses cdecl. Each
frame has a monotonic ID. Dynamic probe entry is installed only from an observed
successful named/ordinal GetProcAddress return. No address is borrowed from the
debugger process.

The original DLL recursively calls its exported probe through a volatile
function pointer. Two threads each invoke depths0–3. Subject assertions compute
the independent closed-form result, both pristine and traced. The recorder must
show25 loader/export pairs plus20 actual probe pairs, including recursion depth4,
two calling threads, failed lookup returns, and all exact arithmetic results.

Return sites remain installed until process exit, permitting shared sites across
threads and recursive frames. A stale site with no matching frame is stepped
without inventing a return. Known entry/return-address collisions fail admission.
Wrong return ESP, non-LIFO returns, stack unwind, pending calls at thread/process
exit, slot/depth/request/event/time bounds and access failures invalidate the run.
Other threads are suspended only while restoring/single-stepping/rearming one
instruction, retaining and releasing the recorder's own suspend increments.

Limits: 64 threads,32 frames/thread,128 breakpoint addresses,4096 calls,10000
events,60 seconds. Fixture DLL is intentionally retained until exit. This is not
qualification for arbitrary DLL unload/reload, exceptions/unwinding, tail calls,
all calling conventions, COM interfaces or game behavior. No call duration/FPS
is measured. The portable pairing tests exercise exact shared code but do not
prove Windows breakpoint transport. Fresh NT5 execution and cold audit are
required independently. The Xbox and delivered ZIPs are untouched.

Space recovery archives only closed leaf evidence after fresh dependency inventory,
recorded closure/cold-hash checks, and decompressed SHA/length verification before
removing exact original paths. Nothing is resumed or used as a new parent.
