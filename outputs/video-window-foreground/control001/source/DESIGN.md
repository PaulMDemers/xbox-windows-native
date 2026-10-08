# Matched ordinary movement with explicit test-window foreground

Use unchanged RAM0110/control and RAM0112/candidate, same immutable parent and shared
probe138. Prior ordinary control failures remain FALSE. Pixel inspection localized
all differences to x270..383/y100..255, where the Windows Getting Started window
visibly covered the scene. This probe raises ONLY its owned parent before each
measured interval with SetWindowPos(HWND_TOPMOST). It does not dismiss, cancel or
alter any other window, device or startup policy. A200ms settle/pump occurs before
counter snapshots. Same strict pixel/event/integrity gates; no failure waiver.

18 actual128x80 child moves with real bitmap/TextOut, behind96x144 fixed child,
six positions repeated3times including negative/partially outside positions.
Each move readback precedes an independently measured forced full child repaint.
18 CPU-composed references plus36 actual screen readbacks and checked font bitmap
are saved and cold-verified. Primary readback+RAM/scanout check uses candidate code;
not independent physical scanout proof. Font glyphs are guest-produced, cold checked
for bounding/color/nontext invariants and required identical across both runs.
No independent raw cursor verification: cursor placed during movement then hidden
before pixel readback. Retain native paint counts, callback/byte counters, geometry,
quiet intervals and coarse GetTickCount milliseconds. Shared host execution is not
performance isolation; report bytes, never infer physical FPS from timings.

Require normal shutdown/dashboard, full allocation,5structural hives, protected
binaries, expected inherited null-device/unsupported-device policy, unchanged
pagefile/configuration and no warning/error/application deltas. Unique attempts,
one launch and one collection each. No debugger or physical access.
