# Same-primary copy348 compiled

Exact345/303 parent tree e48e031228a0d6d483c7ac8273c40a34b75644e7, fresh private
source checkout and matched RosBE2.2.1 builds. Only XWN_PRIMARY_COPY differs;
profiling, HD/text bounds and all other settings match. Candidate replaces only
eligible same-PDEV primary32bpp CopyBits with bounded RAM row memmove. Upload,
mapping/cache policy, allocation/lifetime and all other drawing hooks are
source-identical. This targets the measured engine component, not a claimed
fix for the larger uncached-upload cost. No extra screen-sized allocation.

Actual-source host002 adapter/planner passes53291 ASan/UBSan checks per mode,
13299 pixel/preimage/guard cases each,35 refusals each. Includes all relative
displacements of3x3 inside8x8, randomized clipping/overlap and1920x1080 cases.
Host membership/SURFOBJ ABI is modeled; host libc is not the guest memmove.
The first host001 passed the same checks but its low-byte RNG had a256-byte
period. Its unchanged files/results are retained. Host002 uses the high byte
to avoid that weak pattern; helper/adapter bytes are identical. A PowerShell
inline generation quoting failure made no files; strengthen-host.py performed
the explicit guarded generation instead.

Compiled PE checks pass: actual owned NT5 imports unchanged, resident adapter/
copy/stats routines, candidate local memmove call absent in OFF adapter, no
SIMD/FPU instructions in the new adapter, equal warning multisets. Source
review independently confirms old scanout uses local libcntpr aligned REP
MOVSD, not an imported or byte-only copy. No scalar-unroll209 repeat or unsafe
cache-type change. Existing late-cache review remains historical evidence,
not a fresh1080 physical page-table audit.

The new probe retains344 operations and independent pixel/guard oracles, adding
only read-only348 coverage packets outside timing. It compiled warning-free;
all imports resolve in owned NT5 providers. review-build.py's workspace root
was corrected for the new nested probe directory before execution; generated
initial source-review records the original path-only version. Compiler inputs
and exact binary are pinned in probe/build001.json and build-review001.json.

Fresh349 emulator validation is now closed. Independent pixels/audio, normal
shutdown and cold integrity passed in both cases. Smaller overlap copies use
the fast path fully;960x540 copies have eight fast and five fallback calls per
operation,6036 bytes short of the full-fast-byte requirement. Candidate coverage
and matched qualification FAILED. Read ../primary-runtime349/REPORT.md for the
preserved parser failures and exact accounting. No physical access,
installed-driver change, speedup or release promotion follows from these results.
