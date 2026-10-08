# Display lifecycle research: supported desktop experiment selected

The next discriminator is a supported desktop create/switch/close operation with
exact drawing/readback before, during and after. See ../video-desktop-lifecycle.
This is a hypothesis about coverage, not a claim that a desktop is a PDEV.

Owned Windows 2000 win32k.sys is SHA256
414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92,
timestamp4BDE868A, SizeOfImage192E00. Its separate-debug record is MISC type4,
with sys\win32k.dbg in the file-offset payload; AddressOfRawData is not a usable
RVA for this record. No CodeView PDB identity is embedded. owned-images.json
records exact raw debug data plus actual owned user32/gdi32 export identifiers.
These are static export facts, not private Win32k symbols or runtime call proof.

The exact Microsoft symbol-server key4BDE868A192e00 returned404 for win32k.dbg,
win32k.db_ and file.ptr. Both fetch records are preserved. This does not prove
symbols do not exist elsewhere. No another-build symbols or speculative internal
names were substituted. Matching NT5 exports suffice for an API experiment; its
driver callback observer can use our own pinned COFF symbols later.

Microsoft's CreateDesktop documentation requires NULL device/DEVMODE reserved
arguments and DESKTOP_CREATEWINDOW access. SetThreadDesktop requires no windows
or hooks on the departing thread. SwitchDesktop needs a visible window station
and switch access. CloseDesktop must not receive the borrowed GetThreadDesktop
handle. These constraints define the new harness. The documentation identifies
Windows 2000 support; probe import review separately verifies the owned DLLs.

Already measured: CDS_RESET of the sole enumerated1024x576x32 mode keeps the same
PDEV/surface and only toggles DrvAssertMode. Real boot-video crash takeover also
keeps RAM ownership identity and does not call the watched deletion callbacks.
Neither qualifies surface destruction/recreation. A same-mode reset repetition,
invented unsupported mode, direct DDI call or a guessed Win32k address would not
answer the remaining question. This research changes no guest/hardware settings.

Primary sources accessed2026-10-08:
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createdesktopa
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setthreaddesktop
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-switchdesktop
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-closedesktop
- https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvenablepdev
- https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvdisablepdev
- https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-changedisplaysettingsa
