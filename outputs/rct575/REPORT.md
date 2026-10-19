# Native scrolling control575: both modes qualified on PC

The native helper completed the input comparison with visible landscape
movement, restored Window mode and restarted Windows normally. The only game
helper change from574 was a ten-second settling interval after each builtin
Screenshot. Its measured waits were10,110/10,110/10,110/10,093ms.

| Case | Observed landscape behavior | Changed pixels in630x390 region |
|---|---|---:|
| Window right edge | Stationary | 0 |
| Window right arrow | Moved | 187555 |
| Window right-button relative drag | Moved | 176446 |
| Fullscreen right edge | Moved | 104982 |
| Fullscreen right arrow | Moved | 203730 |
| Fullscreen right-button relative drag | Moved | 213444 |

These counts support visual inspection of displaced paths, fences and trees;
they are not frame rates or scrolling-speed comparisons. One edge, arrow
direction and drag trajectory were tested. The scene was paused. Captures and
input positions were640x480; Window used an800x600 desktop, fullscreen640x480.
Options showed edge scrolling enabled. Owned foreground-window checks and both
HWND reacquisitions passed. No host game input occurred after PREP submission.

All fifteen native captures are valid and nonuniform. Four fullscreen PCX files
match their original game-directory files. Independent passive QMP frames match
207900-pixel landscape regions including the centered notification area, with
no channel difference above eight (allowing display quantization). The matched
full-drag image visibly shows the shifted fence after the arrow scene. These
are sampled display observations, not continuous scanout proof.

The additional pause resolves the earlier unchanged drag in this control and
supports screenshot-notification interference as its explanation. It does not
prove that interception was the sole cause.574's unchanged drag and573's black
fullscreen remain preserved. No game executable or functional driver changed.

Cleanup passed: graceful game exit0, no forced termination, desktop restoration,
exact game registry restoration, five clean independently checked hives and one
new EventLog6006. VM exit0 at09:46:43UTC had no host quit, deadline or passive
capture error. Parent/media remained exact. Cold audit and collection ran once.
The initial display-settings confirmation timed out and reverted before game
launch; the second settings acceptance was visibly confirmed. PREP ran once.

This PC runtime is CLOSED. The native probe is qualified for a separately owned
Xbox comparison with fresh staging, pins, startup-hook cleanup and cold evidence.
The Xbox itself has not been accessed;565 remains its latest result. No physical
input, GPU acceleration, game-FPS, sound or cross-restart save claim is added.
