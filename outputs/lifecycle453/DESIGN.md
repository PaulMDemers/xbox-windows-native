# Bounded DirectDraw lifecycle sample

The unchanged working desktop and driver remain the baseline. Two ordinary
processes request default and HEL DirectDraw7 separately. Each performs eight
warm-up cycles then64 measured cycles, holding at most two128x96 RGB32
SYSTEMMEMORY surfaces (98,304 nominal pixel bytes) at once. Each cycle writes
independent coordinate colors, copies a rectangle, checks every source and
destination pixel including untouched guards, then requires both Release values0.
The measured capture is6,291,456 bytes per process, independently reconstructed
by the Python oracle. A90-second external controller bounds each process.

A malformed zero-size descriptor must fail without returning a surface; subsequent
valid allocations exercise recovery after that refusal, not OOM recovery.
The first measured pair remains allocated across three actual focus acknowledgments
between two owned windows. GetActiveWindow/GetFocus and WM_SETFOCUS establish
calling-thread state only; no global foreground or external-dialog action is claimed.

PSAPI GetProcessMemoryInfo is resolved from the installed DLL. After warm-up,
PagefileUsage growth must remain within a predeclared1MiB budget; every measured
post-release query is recorded alongside working-set values. This is a bounded
process-memory observation, not proof of leak freedom or kernel/driver accounting.
The owned NT5 PSAPI export is pinned, and the actual PC fixture must match before
launch. No memory pressure, deliberate OOM or unsupported allocation stress occurs.

IsLost must report DD_OK for this unchanged-mode system-memory control. An actual
lost surface refuses this scope; it is not disguised as successful restoration.
Microsoft documents that DD_OK means the allocation is not lost, and Restore
reallocates memory without restoring bitmap contents:
[IsLost](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawsurface7-islost),
[Restore](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdrawsurface7-restore).
Actual loss/restore is a separate future scenario. No GPU/D3D qualification follows.

Use a fresh private child of the pinned404 clean NTFS source, immutable test
floppy, completed preflight before launch, actual UI state, normal guest restart,
closed-process cold audit and independent NTFS-3G extraction. No console launch
until this PC control qualifies. Preserve all failures and never rerun a used ID.
