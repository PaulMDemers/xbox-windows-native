# PC569 CLOSED: native helper rejected after the first click

The native input comparison did not qualify. The one GDI capture passed BMP
structure checks, but it showed the licence splash rather than the title menu.
A shell taskbar and Start balloon covered the lower client area. The attempted
New Game click at screen233,470 was followed by loss of game foreground, and
the helper stopped sending the sequence. Later QMP images show a command-window
system menu over the game. No scrolling case was reached. Why the taskbar
retained its earlier position after the helper display change remains unknown.

The cleanup path passed: game exited0, no forced termination, exact registry
subtree restored, prior PC display mode restored, five hives clean and one new
6006 normal-shutdown event. VM exited0 at07:40:59UTC without host quit/deadline.
Source404 and helper ISO remained exact. This does not qualify game input,
fullscreen capture, Xbox behavior, performance or acceleration. All owned
VM/audit/collector processes are closed; Xbox was not accessed.

Build001's compiler-warning failure and exact input source are retained;
build002 compiled without warnings. A screen request after QEMU exit raced the
supervisor's final hashing; ownership guard refused before QMP, with no relaunch.
The capture reviewer emitted a Pillow getdata deprecation warning, not a test
failure; use get_flattened_data in subsequent tooling. Never rerun, recollect or
parent this closed runtime. Retain private disk, captures, hives and game files.

Next fresh control: minimize only the helper's console, verify WindowFromPoint
belongs to the owned game before each mouse input, allow the title splash to
finish, and prepare the PC800x600 desktop through the already observed display
UI before launching. Omit helper-driven desktop changes; physical720p stays
protected. Independently inspect the new captures before console admission.
