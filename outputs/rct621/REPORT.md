# PC621 closed matched saved-scene instruction-location result

Fresh immutable404 child ran2026-10-20T20:20:44.994611Z to20:28:26.087964Z.
One game launch followed1024x768 setup,503-file copy verification and readback
that both CDs were ejected. No host captures/input or sample-log writes occurred
during the measured interval. Windows restarted without host quit/reset.

## Result

Over20.094 guest seconds (20.095143685 host), RCT used20.046875 CPU seconds:
13.78125 user and6.265625 kernel. The actual CreateProcess main thread accounted
for exactly20.046875 seconds. Observer CPU increment was0 at coarse resolution;
this does not establish zero overhead. Five-second sleep matched4.982119002 host.

240 balanced main-thread snapshots:73 RCT,88 WINMM,78 ntdll and1 GDI32.
All prior suspension counts were0, resumes1; largest measured hold0ms at coarse
tick resolution. Module maps were stable. The qualified620 primitives/loop were
unchanged; fifteen host rejection cases passed. Runtime code bytes and kernel
stacks were not captured; these counts are not CPU-time percentages or FPS.

Exact immutable-seed DLLs match the closed621 protected-file manifest. Their
exports and instruction boundaries map69 WINMM samples to timeGetTime's body
and19 to its directly called arithmetic helper. All78 ntdll samples map to the
NtSetInformationThread/ZwSetInformationThread syscall-return site; the single
GDI32 sample also maps to an internal syscall-return site. These do not identify
kernel costs or establish sleeping. The73 game RVAs remain unnamed because its
packed on-disk code is not a substitute for runtime code bytes. See
site-symbols001.json and cost-review001.json. Timer polling is the next concrete
lead, not a proved cause or justification for a timing/driver patch.

The saved scene matched all165600 reference pixels before and after timing.
The earlier right-moved view changed76850 pixels and reloading restored them.
All nine private captures were inspected: title, scenario/objective, Window
options, moved view and restored entrance scene rendered without visible error.
The exact saved file stayed unchanged. No physical Xbox test or acceleration
claim is made. Pristine615 and recorded618 remain separate single PC intervals;
621 does not isolate total sampling overhead or measure game FPS.

## Closure and retained failures

Cold audit:7003 files/315 directories, five clean hives, exact tools/save/OS/seed,
registry restoration, one new normal EventLog shutdown and no forced game exit.
All owned VM/build/cold processes closed. The immutable-seed DLL export is a
small read-only operation;621's closed runtime was never reopened.

Keep build001's missing-header failure, host-tests001's incorrectly constructed
negative input, missing copy_contract imports, copy-contract-tests002's wrong
historical build reference and the preparation script's existing-file guard.
Corrections were host/preparation-only before the single retail launch. Actual
build002, host-tests002, media-review002, copy-contract-tests003 and scene-tests001
passed (corrected scripts wrote first successful media-review001 and
copy-contract-tests001 receipts). close001 misnamed those receipts; close002
corrected only filenames and retained every gate. A post-run attempt to read unexported WINMM failed before any disk access;
three exact DLLs were then read from immutable404, not the closed621 runtime.

619 remains a closed prelaunch failure with normal cleanup.620 remains closed
PASS. Their archive receipts preserve closed618/616/617/610/614/593 raw leaves
with full roundtrip hashes. Do not reopen/recollect/parent closed runtimes.
No physical access: Xbox last dashboard/no owned hook;596 SOFTWARE cleanup is
cold-only. Protected720p, ordinary launcher, packages and paused automation
remain unchanged. Sound, fullscreen/input, other consoles and boot issues remain
deferred. No hardware input needed for this completed host milestone.
