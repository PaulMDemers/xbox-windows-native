# Observe clipping before changing the uploader

Fresh candidate001 uses the immutable RAM0110 parent from video-line-gdi. No driver,
settings or device policy changes. Probe132 uses real GDI PatBlt requests and an
independent DIB reference, then cold host-generated union-of-rectangles references.
Six cases repeat three times: two distant islands, overlapping regions, offscreen
rectangles, an empty visible intersection, sixty islands, and two consecutive draws
with the same selected region. Each screen draw is bracketed by explicit markers.

The bounded debugger observes XwnBitBlt and actual win32k CLIPOBJ_cEnumStart/bEnum
exports, paired by thread and exact stdcall stack. Capture counted buffers including
the final FALSE return, clip identity, owned surface and code pins. No guest memory
or register mutations. All breakpoints must be removed before runner cleanup.
The absence of calls is missing enumeration coverage, never permission to infer it.

Microsoft's API contract specifies CT_RECTANGLES, a restartable enumeration,
FALSE on the final batch and possible TRUE with zero rectangles. Runtime evidence
must establish what this exact NT5 build does. A future uploader must remain bounded
and fall back conservatively on incomplete or invalid enumeration. No optimization
is included in this diagnostic. References:
https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-clipobj_cenumstart
https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-clipobj_benum

The prior line diagnostic's late kernel32 header E14 remains a failure. This new
observer explicitly records an unreadable kernel32 header and still requires the
loader identity and exact relocated resident entry bytes and cold binary hash.
It never substitutes an unreadable code entry with a guessed pin.

Require complete18-case pixels, cold allocation/hives/protected hashes, unchanged
pagefile/configuration, zero warning/error/application events and normal dashboard
return. Debugger timing is separate from ordinary qualification and hardware.
