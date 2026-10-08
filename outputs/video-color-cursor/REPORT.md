# RAM0109 ordinary color cursor lifecycle PASS

Fresh candidate001 completed 26 actual GDI operations with two authored 32x32
color cursors. Each case drew beneath the first cursor, hid it with
SetCursor(NULL), showed the replacement at the same position, then moved it
away. GetCursorInfo required the exact handle, visibility and position at each
stage. Hotspots were (7,11) and (15,3). Both color bitmaps used top-down 24bpp
pixels and explicit transparent mask stripes. Source bitmaps were unselected
before CreateIconIndirect and deleted after it copied them.

All 2,555,904 RGB pixels in restored-background readback matched independent DIB
references. All 78 cursor-state phases, source/reference immutability, zero
callbacks during reference rendering, 26 scanout coherence checks and 26 exact
cold reference files passed. The callback interval includes drawing and cursor
operations; its 247 CopyBits calls are not individually attributed to a caller.

Normal shutdown count 1 and dashboard return. Full allocation: 325 directories,
6,785 files, 326 directory clusters, zero errors/orphans. Five structural hives,
protected binaries, installed payloads and startup hashes passed. The 96MiB
pagefile and inherited configuration are unchanged. No new warning/error or
application events. Eighteen mutations of the actual log were rejected.

See verification.json, protocol-tests.json and candidate001/audit.json. The
initial compiler-rejected indentation is preserved in probe-build-failure001;
it produced no guest run. The corrected probe passed the existing -Werror and
actual Windows 2000 import review. Ordinary candidate001 is CLOSED and must
never be relaunched or recollected.

Probe123 SHA256: c00a46bbf5391532ad43e8a0c29c1475439b47800f0972f6e1dd262cd350ef57.
Unchanged RAM0109 SHA256: ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440.
No debugger, UI intervention, driver/cache/policy change or physical access in
this ordinary run. Independent visible-pixel evidence is recorded separately
in video-color-scanout. Alpha/animated cursors, ShowCursor display counts,
lifetime races and display-mode transitions remain outside this qualification.
