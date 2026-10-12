#319 prelaunch debugger transport failure, closed

No Windows launch was requested; no breakpoint was installed. The initial raw interrupt timed out and so did the original teardown interrupt. Cleanup-only HMP showed the VM was paused. A separate explicit GDB ? query returned T05thread:01 and physical mode0; monitor cont resumed the guest, then the owned runner stopped/quit with exit0 and no fallback. The failed original trace remains unchanged.

Cold verification found every original fixture file byte-identical, no workload log, five valid hives and clean322directories6752files323clusters/zero errors/orphans. No ordinary or loader-state evidence.320 is a new private run from the same unused immutable preparation with corrected initial handshake, never a child of this runtime.
