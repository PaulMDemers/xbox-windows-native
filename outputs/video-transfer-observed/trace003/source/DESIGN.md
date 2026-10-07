# Bounded installed drawing-path observation

Unchanged video0093/Microsoft framebuf and qualified emulator storage/network
stack. Fresh child and unique probe outputxwnvid107; no physical console access.
The corrected GDI profile gains an exported noinline marker around ONLY the
first upload and overlap precheck at64x64 and768x384. Markers bracket the public
BitBlt operation and following GdiFlush. Full54 cases/162pixel stages, normal
restart and cold/event gates remain; debugger run is not ordinary qualification
and its timings must not be reported as performance evidence.

Before launch, arm only the marker address. At actual probe context, validate
process, PEB module list and resident bytes. Resolve kernel Win32k service table
using the pinned kernel symbol and actual syscall numbers from the owned GDI
stubs (100d and1093). Observe paired user BitBlt/GdiFlush, kernel services and
EngBitBlt/EngCopyBits/EngStretchBlt if executed. Gate on the same thread and
sample; pair entries/returns by address and expected stack. Record bounded public
SURFOBJ/clip/rectangle bytes, module identities and code pins. Never patch
arguments, return values, drivers or device policy.512stops/600seconds maximum;
remove ALL breakpoints and resume on success or failure. Preserve incomplete
capture and then collect the single run after normal dashboard return.

The pre-existing batching limit is1. Microsoft documents that this disables
batching for the thread; GdiFlush is not a universal GPU fence:
https://learn.microsoft.com/en-us/windows/win32/api/wingdi/nf-wingdi-gdiflush
Use the actual NT5 stubs/service table, not contemporary syscall numbers.
Public surface concepts are documented at
https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-surfobj
but current definitions include extra fields; the pinned historical x86 layout
and runtime dimensions/stride must agree before interpreting captured fields.

Success means a paired route for all four selected operations and flushes,
resident identity checks, complete teardown, correct pixels and clean cold audit.
Absence at an export only rules out that observed export during the bracket;
internal software routines may bypass exported Eng wrappers. No inference of
physical speed, hardware acceleration, generic PnP lifetime or scanout correctness.

## Observer revision

Previous trace001 completed the two small samples then failed an E14 read. It
removed all breakpoints and resumed; do not count that as four-route success.
This fresh trace003 retains explicit failing read address/length/call stack and
last registers. PE identity headers are validated once per loaded module in the
fixed probe lifetime; every observed entry/return still requires exact relocated
resident code bytes. The captured header identity is referenced by each pin.
This avoids unnecessarily requiring an already-validated PE header page to stay
resident; it does not page in memory or skip a failed code-byte check. The old
failure's exact read was not logged, so header eviction remains a hypothesis,
not a proven explanation. Same compiled probe and no driver/configuration change.

Trace002 preparation failed before a fixture or guest existed: source-copy filter
omitted probe.c. Retained prepare-failure.json; trace003 uses the exact original
probe source/binary. This host failure is distinct from trace001 E14 capture.

The two complete trace001 samples both reached EngCopyBits with32-bit bitmap
surfaces. Trace003 also observes six bounded call sites inside that exact pinned
EngCopyBits implementation, including its two indirect copy dispatches. Actual
register/memory operands determine the target; record resident target bytes,
callsite/return pairing and bounded raw argument context. These are address-based
observations, not speculative symbolic names for private Windows routines.
