# RCT597: qualify an API-request recorder before tracing the game

This attempt tests original synthetic programs on a fresh immutable404 Windows
2000 PC child. No Xbox access, game launch, driver change or performance claim.
The recorder uses DEBUG_ONLY_THIS_PROCESS, stops at the loader breakpoint, reads
the target's two pinned IAT slots and places process-local INT3 breakpoints at
LoadLibraryA and GetProcAddress. It records entry arguments, not return values.
Consequently these are API requests, not successful resolutions or method calls.

On an owned breakpoint it reads the stack and bounded string, restores the
instruction, rewinds EIP, sets TF, and suspends other live threads until the
single-step event rearms the breakpoint. New threads during that interval receive
an owned suspend increment. Only those increments are resumed. Unknown exceptions
are passed to the target. All memory reads/writes, protection changes, cache
flushes, contexts and debug continuations are checked. Failure terminates only
the newly created target; no detach with patched instructions is supported.

Known subject calls include repeated and concurrent named resolutions, a named
missing export, valid and invalid ordinal requests, and a missing DLL. Its own
receipt checks return values and invocation results. Compare that receipt and
the exact request multiset against a separate uninstrumented control. A bounded
runner then requests normal Windows restart. Trace timings are never game FPS.

This first recorder intentionally does not follow DirectDraw interfaces. RCT's
actual API requests, resolution returns, surface methods and their costs remain
later work after this recorder's NT5 behavior is checked. All private payloads
and screenshots stay outside the public repository.

API reference: Microsoft's [debugger loop](https://learn.microsoft.com/en-us/windows/win32/debug/writing-the-debugger-s-main-loop)
documents suspended debug events and instruction-cache flushing after code writes.
Current documentation is not itself proof of Windows 2000 compatibility; the
fresh fixture supplies that check.
