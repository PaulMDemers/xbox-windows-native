# RAM0109 ordinary monochrome cursor restoration PASS

Fresh candidate001 completed all26 real GDI cases under an authored visible
32x32 monochrome cursor. Hotspot7,11; four AND/XOR quadrants; positions80,70;
0,0 (desktop clipping);380,250 (test-rectangle clipping);170,140. Exact cursor
handle, visibility and position required before each draw and after moving away.
Same probe122 and unchanged RAM0109 driver are used by the separate diagnostic.

All2,555,904 RGB pixels after moving the cursor away match independent DIB
references. Source/reference hashes, zero callbacks during reference rendering,
26full-frame coherence checks and26cold reference files pass. Actual callback
totals include174CopyBits across draw and cursor movement intervals; those totals
do not attribute every call to a specific cursor routine.

Normalshutdown1 and dashboard return. Full allocation325directories/6785files/
326directoryclusters, zero errors/orphans. Five structural hives, protected and
installed payload hashes, startup, unchanged pagefile and configuration pass.
No new warning/error or application events. Sixteen actual-log corruption tests
are rejected. See verification.json, protocol-tests.json and candidate001/audit.json.

Probe SHA25602bc4a802a8717e08ce2cfccebec4cba99d7ee9a0148ecd001f7c0595ccf8cf0.
Driver SHA256ed901376d61e70a125fce834e20b366e49a1d632879debbcfedd621c18b6a440.
Build/source/fixture and closed disk hashes are retained. No debugger, UI input,
driver change, physical access, mode or cache-policy change in this ordinary run.
One read-only running framebuffer progress snapshot is retained privately; it
is not used as a pass oracle. All owned ordinary processes are CLOSED.

GetCursorInfo establishes cursor state, not independently verified visible
cursor pixels. The separate video-cursor-scanout experiment addresses that gap.
Color/animated cursors, pointer lifetime races, mode/boot-video transitions and
physical performance remain unqualified. Four earlier unobserved GDI callbacks
remain unobserved here. Never relaunch or recollect this closed candidate001.

The authored mask follows Microsoft's [cursor mask truth table](https://learn.microsoft.com/en-us/windows/win32/menurc/using-cursors).
Actual NT5 behavior is tested against the pinned guest rather than inferred from
current DDI documentation's obsolete-pointer-return guidance.
