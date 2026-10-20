# PC597–599 closed: request discovery complete; actual drawing calls next

PC597 passed the original synthetic recorder control: 25 requests across two
threads, matching subject return/invocation checks with and without tracing,
normal restart and cold audit. Its first compiler failure remains preserved.

PC598 failed its display setup: requested 800x600x32 returned BADMODE(-2), but
the helper continued at 640x480 until the visible-client guard rejected input.
Its 332 API entries remain useful discovery evidence; park/input stayed failed.
Normal close/restart, registry restoration and cold checks passed.

PC599 corrected setup through native Display Properties, confirmed 1024x768 at
16 bits, and checked actual metrics before game/registry changes. Title, named
Forest Frontiers objective and paused park captures passed. All five BMPs are
valid. Game/debugger exited0 without forced termination; registry absence and
normal restart/cold audits passed. One automatic screenshot raced normal VM exit
(FileNotFoundError, process_exit0), retained in the record. No rerun/recollection.

Both game attempts captured 332 requests: 237 RCT-image callers and95 other DLL
callers. Main library/export counts agree. RCT requested DDRAW.DLL,
DirectDrawCreate, DirectDrawEnumerateA/W and GDI exports including BitBlt,
StretchDIBits/CreateDIBSection/palette operations. Entry arguments are NOT
successful resolution returns, drawing invocations, surface types, FPS or GPU
evidence. No matched pristine game control or overhead measurement yet.

Next: NEW bounded synthetic control for paired function returns and actual
invocations, including recursion/thread interleaving and failure cases. Then a
fresh game fixture observing DirectDrawCreate results, returned interfaces,
surface descriptions and actual GDI/DirectDraw update calls. Qualify the retained
593 save as a fixed loaded scene before timings; pair uninstrumented/instrumented
game controls and quantify overhead. Do not repeat manual save/load compatibility
solely to replace the user's confirmed596 result. No functional driver patch.

All owned host processes are closed; all597–599 runtimes are CLOSED and must not
be reopened or used as parents. Xbox untouched this turn, last at dashboard with
no owned hook. The596 offline SOFTWARE cleanup is still cold-only, awaiting a
subsequent Windows boot. Existing saves, launcher, protected720p and both delivered
ZIPs remain unchanged; no RCT in those ZIPs. Other consoles, sound, fullscreen,
boot intermittency and1080i stay deferred. Automation remains paused.

C: about20.26GiB free; E: about26.52GiB. No new VM/large allocation before capacity
recovery and projected reserve checks including WSL backing.597 already archived
closed572/566 leaf disks losslessly to E:/xwn597/archives, verified decompressed
SHA/length and excluded recorded backing references before exact original removal.
Those are evidence archives, never resumable runtimes. Preserve private256/release
rollback and all failed evidence. Public review/staging/commit status is recorded
in the final turn message; never infer a push from these notes alone.
