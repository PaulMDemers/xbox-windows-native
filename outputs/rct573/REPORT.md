# Native input control 573: windowed controls work; fullscreen remains unresolved

The scan-code arrow and relative-mouse changes produced visible landscape
movement in Window mode. The right edge still left the view stationary, with
edge scrolling enabled in Options. This agrees with the earlier device-input
[PC568 comparison](../rct568/REPORT.md), but does not add a physical Xbox result.

All sixteen capture calls completed, and the input-submission contract passed.
Independent inspection prevents treating that as a complete gameplay pass:

| Case | Observed result |
|---|---|
| Window right edge | Same landscape; zero changed pixels in the measured region |
| Window right arrow | Landscape visibly moved; 115,967 changed region pixels |
| Window right-button drag | Landscape visibly moved; 174,806 changed region pixels |
| Fullscreen Options and all four scene captures | Entirely black; unusable for per-case movement evidence |
| Restored Window mode | Options and landscape visible again, with a different camera position |

The measured region is 630 by 390 pixels. Counts are supporting comparisons,
not frame rates. The five fullscreen BMPs each have one RGB value and identical
hashes. A passive QMP screenshot during the fullscreen interval is also black
(`auto-1792400424685241061.png`); therefore this is not established as merely a
GDI readback limitation. Capture interference, display state and timing remain
possible explanations. The changed view after returning to Window mode does not
identify which fullscreen control moved it, or prove that it was visible then.

The helper reacquired exactly one owned foreground game window after each mode
change. Fullscreen geometry was 640 by 480 at origin 0,0; Window geometry returned
to 640 by 480 at 36,55 on an 800 by 600 desktop. Both arrow holds recorded scan
code 77, flags 9 and an observed asynchronous down state. These receipts support
the harness operation, not the missing fullscreen rendering evidence.

Cleanup passed: graceful game exit zero, no forced termination, desktop restored,
exact game registry restoration, five clean independently checked hives and one
new EventLog 6006. The VM exited at 09:01:15 UTC without host quit or deadline.
The immutable parent and helper ISO stayed exact. Collection ran once and all
owned processes are closed. No Xbox access or temporary startup hook occurred.

The next control should preserve these input methods and remove fullscreen GDI
capture as a variable. The supplied Deluxe manual documents a built-in Screenshot
command that saves to the installation directory (PDF page 31, printed page 61).
A retained PC568 image shows that command in the file menu. Validate its actual
file output and compare it with passive emulator images in a fresh fixture;
do not infer a working display from a game-generated screenshot alone.

This runtime is CLOSED. Its complete-matrix qualification is false despite a
passing submission contract. No Xbox, GPU, FPS, sound or save/reload claim is made.
