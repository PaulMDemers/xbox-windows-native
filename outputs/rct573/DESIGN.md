# Fresh native input control573

572 reached the park but the native arrow/drag inputs left its view unchanged.
Switching display mode invalidated the cached game HWND and correctly stopped
the sequence. This successor uses scan-code extended arrow input, relative
mouse events during right-drag, and bounded unique owned-window reacquisition
after mode changes. It never changes the game executable or display driver.
Input success remains a harness observation; private captures must demonstrate
the actual scene and movement independently. No Xbox launch is admitted here.

The helper retains PID/class/focus/bounds/occlusion guards, releases inputs,
restores temporary registry values and closes/restarts on completion or failure.
Reacquisition does not force foreground or relax dimensions. A fresh immutable404
child is required. Closed572 and all earlier failed controls remain preserved.
No host game input after starting PREP.CMD. Time and projected20GiB reserve
including WSL backing storage must pass before allocation. No overnight reset.

Primary API references:
- [KEYBDINPUT](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput)
- [MOUSEINPUT](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput)
