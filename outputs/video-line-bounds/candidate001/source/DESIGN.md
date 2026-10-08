# Observe real NT5 cosmetic line bounds

New emulator-only child and probe129; unchanged RAM0109, no driver/settings edits.
Eighteen real GDI samples cover horizontal/vertical and45-degree diagonal lines in
both directions, offscreen endpoints, tight and complex clips, right-edge clipping
and a zero-length line. Endpoint exclusion and clipped pixels have an independent
host oracle in addition to the guest DIB reference. No arbitrary-slope rasterizer
equivalence is claimed. Empty output is intentional only for the zero-length case.

Two exported user markers bracket each primary draw. Only within those intervals,
observe actual XwnLineTo entry and stdcall return; capture the raw ten-DWORD stack,
signed line/bounds values,24-byte CLIPOBJ and52-byte SURFOBJ and ownership table.
Pair by thread, return address and expected ESP+40. Pin actual relocated resident
entry/return bytes and loaded module identities. Do not infer an invocation when
GDI routes another path or elides a zero-length operation.

Layouts are the owned compiled winddi.h: SURFOBJ dhsurf0,hsurf4,dhpdev8,hdev12,
dimensions16/20,iType48; CLIPOBJ rectangle4..19,complexity20. Bounds RECTL is four
signed32-bit coordinates. Keep raw bytes, stages, calls and CPU state for verification.
Bounds must contain independently predicted changed pixels before considering a
future upload optimization; no driver change is made in this diagnostic.

Capture bound600seconds/384stops/64calls, observed single-step progress, all
breakpoints removed and guest resumed on exit/error. Observe actual ExitProcess;
supervisor waits for trace-closed before runner cleanup. Complete cold allocation,
18exact RGB images, five hives, protected hashes, pagefile/config, normal shutdown
and strict events remain required. Debugger qualification is not ordinary or
physical qualification. Never relaunch/recollect this case. Preserve all failures.
