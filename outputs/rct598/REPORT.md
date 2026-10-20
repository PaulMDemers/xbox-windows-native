# Closed display-setup failure with retained startup API evidence

The helper's800x600x32 request returned DISP_CHANGE_BADMODE(-2). It continued at
640x480; the strict visible-client guard then rejected the632x453client extending
beyond the desktop. No input sequence or park capture passed. This is a harness
failure, not an RCT regression. Fresh599 uses the native Display panel and a
fail-closed1024x768preflight before creating the debugger or touching game registry.

The request recorder itself completed:332API entries,237from the RCT image and
95from other DLL callers. RCT requested DDRAW.DLL, DirectDrawCreate and both
DirectDrawEnumerate variants. It also requested GDI functions including BitBlt,
StretchDIBits, CreateDIBSection and palette operations. These are observed lookup
arguments, not successful resolution returns, drawing calls or acceleration.
The broad startup import requests are insufficient to identify the active renderer.

WM_CLOSE ended the game and debugger normally. Windows restarted; cold readback
found one new EventLog6006, restored absence of the temporary Fish Technology Group
subtree, exact3tools, all502files verified before launch and unchanged protected
OS binaries. The final asset differences remain in asset-changes001.json. No
owned process, console launch or hook remains. A screen request raced normal
exit and the ownership guard refused it; no closed runtime was reopened.

See [final001](final001.json), [request inventory](trace-review001.json),
[cold audit](ntfs-cold1-002.json), and [corrected experiment](../rct599/DESIGN.md).
No game FPS, matched uninstrumented comparison or hardware qualification is claimed.
