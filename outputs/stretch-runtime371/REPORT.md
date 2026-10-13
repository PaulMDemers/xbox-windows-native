# Stretch bounding is correct in the tested path, with no measured write reduction

Fresh matched371 control001/candidate001 completed five samples each, with12 stretch cases and960 actual StretchBltROP callbacks per run. Both passed the added full-window/source/scanout comparisons, all retained drawing tests, audio API/device/captured-channel checks, normal Windows restart and orderly emulator exit0. There were no forced exits. Each closed disk had341 directories,6809 files and358 directory clusters with zero allocation errors or orphans; five structural hives, protected hashes, selected policy/bindings and event/setup history passed.

The candidate uploaded exactly the same bytes as the control in every one of the60 measured case intervals per run:

| Clip | Bytes per16 calls, both builds | Destination orientations |
|---|---:|---|
| None |131072|All four|
| Rectangle |73728|All four|
| Two disjoint rectangles |49152|All four|

Each value equals the independently calculated minimum area for that case. The original path already bounds its effective upload to the destination/clip intersection. This is consistent with a destination-limited clip reaching the wrapper, but no clip-object entry trace was taken. The source's NULL upload-bound argument alone was not evidence of redundant runtime writes. Host369's modeled wider-clip reduction remains valid only for that modeled input; it did not occur in these Windows calls. No byte or hardware-speed benefit was demonstrated, so369 will not be deployed as a performance improvement.

Actual callbacks exercised StretchBltROP, not the separate StretchBlt wrapper. Both wrappers were covered by369 host tests. The new guest source is constant-color: three positive-orientation cases also use a separate geometric oracle; mirrored destination cases compare with a driver-free GDI DIB rendering. These are bounds/clip/content-preservation checks, not exhaustive sampling, mask or ROP validation. Emulator millisecond timings do not establish physical speed.

Strict qualification remains FALSE in both runs because Ftdisk49 on HarddiskVolume1 remains present. No event, service, setting or integrity gate was suppressed. The scoped graphics/audio result does not promote a release or make this an ordinary strict pass.

Control launched2026-10-13 21:20:15UTC and returned21:26:06UTC. Candidate launched21:33:09UTC and returned21:38:48UTC. Both are CLOSED and must never be relaunched, recollected or used as runtime parents. Control's first host audit stopped on the missing large_analysis import. The additive completion wrapper preserved that failure, supplied the pinned existing344 dependency, and proved all earlier output bytes unchanged while completing the unchanged auditor. See AUDIT-DEPENDENCY.md. Candidate used the same explicit dependency.

Final review rehashed both frozen closures, supplemental dependency pins, native binaries, fixtures and all private captures (33, 33 respectively). Source369 is exact303 plus three reviewed files; matched build options differ only in XWN_STRETCH_BOUNDS. Probe370 retains the old suite. All owned build/preparation/emulator/audit processes are closed. Physical Xbox normal E startup, original303 driver, F rollback and dashboard C prohibition remain unchanged; there was no physical access. Immutable tags and paused automation remain unchanged. See NEXT.md for the evidence-driven architectural work remaining.
