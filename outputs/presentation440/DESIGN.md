# Rung03 presentation control

New standalone default and forced HEL processes on a fresh child of the closed404
NT5 install. No mode/driver changes. Four stages: visible, sibling-covered,
moved while covered, uncovered. GDI paints blue guards, black target and magenta
occluder only. DirectDraw copies a separate system-memory pattern through an
HWND clipper to the primary; destination extends outside the child target.
Independent source/GDI readbacks and complete clip rectangles must match exact
predefined pixels. Software readback is not physical scanout or hardware completion.

The caller bounds each process at90 seconds; APIs do not gain individual
cancellation guarantees. Normal guest restart, closed QCOW/file/hive/event audit,
and independent NTFS3G selected reads follow. Preserve failed partial results.
No Xbox launch until the Windows2000 control qualifies.

API contracts: [GetClipList](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawclipper-getcliplist)
and [Blt](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawsurface7-blt).
DONOTWAIT refuses busy work; return/readback does not attest backend idle.

This fresh control explicitly raises the cover with SetWindowPos(HWND_TOP),
records and requires actual sibling order/visibility, and captures covered GDI
pixels before consulting the DirectDraw clip list. It preserves439's original
failed test and does not parent or re-execute its consumed disk. Exact schema2
adds these required observations; all old expected patterns remain unchanged.
[SetWindowPos](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setwindowpos)
controls child Z-order; merely making a child visible did not establish that order.
