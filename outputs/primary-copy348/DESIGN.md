# Bounded primary overlap experiment

347's physical 960x540 copies attributed about16ms to EngCopyBits and24ms to the
unchanged upload. This candidate isolates the former. The upload uses local
libcntpr memmove/REP MOVSD, not an imported or byte-only implementation. The
historical209 scalar upload and182 DIB-source path showed no improvement and
are not repeated. This path instead covers two registered primary surfaces
belonging to the same PDEV, with an exact owned RAM bitmap behind them.

Accept only32bpp, positive tightly packed rows, complete bounded source and
destination rectangles, absent or exactly trivial translation, absent/trivial
or rectangular clipping. Reject foreign devices, system-memory input DIBs,
complex clips, unknown geometry, formats or allocation identity before writes.
Intersect destination clip and translate the source origin by the same offset.
Move downward copies bottom-up; row memmove handles horizontal overlap.
Copy all four bytes, including the unused high byte. No extra full-screen buffer.

Keep the current engine fallback, complete synchronous upload, surface lifetime,
mode, cache type, crash mapping, pointer and other DDI hooks unchanged. Never
skip an upload by guessing pixel equality. Existing CopyBits profile category
will measure the selected CopyBits body (fast path or Eng), so a new runtime
report must label it accordingly rather than falsely calling every sample Eng.
New128-byte read-only escape0x58574438/version348 reports enable/attempt/eligible/
fast/empty/fallback and copied bytes with saturation; counters are outside the
measured body and protected by the existing accounting lock. Matched OFF/ON
builds differ only in XWN_PRIMARY_COPY, profiling ON in both.

Qualification requires independent preimage-based pixel/guard/overlap/clip
oracles, actual adapter refusal tests, compiler/import/residency review, then
fresh emulator control/candidate showing actual fast coverage and unchanged
fallback/pixel/scanout/audio/setup/shutdown/cold/event gates. Physical timing is
required before any speed claim or promotion. Hardware still runs its original
restored DLL. Srv2013/Ftdisk49 remain failures; dashboard C is out of scope.

Contract references reviewed2026-10-13: Microsoft
[DrvCopyBits](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvcopybits),
[SURFOBJ](https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-surfobj)
and [XLATEOBJ](https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-xlateobj).
These describe destination clipping, lower-right-exclusive rectangles, source
origin, bitmap layout and translation; actual NT5 eligibility is separately
checked from the owned runtime and compiled ABI, not assumed from modern docs.
