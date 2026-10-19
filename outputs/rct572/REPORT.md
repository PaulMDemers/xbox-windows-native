# Native input control572: readiness passes, scrolling remains unqualified

The revised title reference admitted the real title menu. Native clicks opened
the scenario picker, Forest Frontiers and Options. All nine private GDI captures
were inspected: the objective and Window setting are visible, with edge scrolling
enabled. The four windowed landscape captures are identical in the measured
630x390 region. Neither the submitted virtual-key arrow hold nor the SetCursorPos
right-button drag demonstrates movement. PC568's device-level controls remain a
separate successful observation; this native injection failure does not invalidate
them or establish an Xbox game defect.

Selecting Full Screen640x480 changed the desktop to640x480 and replaced the game
window. The cached HWND became invalid (PID0, failed rectangle/origin reads), while
the final window enumeration found the same owned process foreground with class
RollerCoaster Tycoon and a640x480 client. The guard correctly stopped before a
fullscreen capture. Thus nine captures exist, not the required sixteen; the
native-input review fails. No fullscreen scrolling result was obtained.

Cleanup passed: game exit0 without forced termination, desktop800x600 restored,
exact game registry restoration, five clean independently checked hives and one
new EventLog6006. VM572 exited at08:46:39UTC without host quit/deadline. The immutable
source and helper media remained exact. The first collection completed once;
all owned processes are closed. No Xbox access or startup hook occurred.

A fresh successor should reacquire the unique owned game HWND after each mode
transition, and test scan-code keyboard events plus relative mouse movement.
These are candidate harness corrections, not proven game fixes. Microsoft documents
[scan-code and extended-key fields](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-keybdinput)
and [relative mouse input](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-mouseinput);
runtime behavior still requires independent captures. Keep failure572 closed.

No game FPS, GPU acceleration, sound, save/reload or new physical-console result
follows from this control. Retail files, screenshots and hives remain private.
