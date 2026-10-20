# Recording RollerCoaster Tycoon Deluxe on the development Xbox

Use the existing **Window** game setting on the protected **1280×720 Windows
desktop**. Keep this session separate from the timed diagnostic runners.

## Recording session

The interactive launcher prepared in [624](../outputs/rct624/DESIGN.md) waits
for the player to quit RCT. It does not move the pointer, change resolution,
close the game on a timer, or restart Windows. Hardware deployment and actual
readiness are recorded separately in `outputs/rct625` and `outputs/rct626`; preparation alone is
not a successful Xbox run.

1. Boot the ordinary Windows entry and wait for the desktop. The revised
   recording attempt installs no automatic game startup entry.
2. Choose **Start → Run**, enter `C:\xwn624-kit\play624.exe`, and launch it once.
   If Windows Getting Started covers RCT, close that window normally.
3. Choose **New Game → Forest Frontiers**, or load your existing saved park.
4. Move around with **arrow keys** or **right-button dragging**. Window-edge
   scrolling is stationary in the tested Window mode. Keep **Window** selected.
5. Record normal play, construction and save/load as desired. Sound is deferred.
6. When finished, quit RCT normally. Wait for the launcher's confirmation that
   temporary settings were restored, then use **Start → Shut Down → Restart**.
   Report dashboard return so the session records can be collected.
   Do not power off during a save.

This is a one-session launcher. Do not repeatedly run it or delete its session
guard. A later session needs its own reviewed launch record. If Windows fails
to start, report the screen and leave the dashboard untouched for collection.

## What the footage can establish

The original development Xbox has run Deluxe's title/menu and Forest Frontiers;
the user confirmed building and repeated manual save/load. Physical run 590 also
recorded windowed arrow-key and right-button camera movement. Describe the
recording as **RollerCoaster Tycoon Deluxe running under native Windows 2000 on
an original Xbox**. Frame rate and native GPU acceleration have not been
qualified; PC profiling numbers are not Xbox game FPS. Other Xbox units remain
untested in this work. The separately delivered Windows ZIPs exclude RCT.

## Why fullscreen remains separate

Physical run 590 selected RCT's **640×480** fullscreen option. The desktop stayed
1280×720 and the game remained alive. Its diagnostic helper detected the missing
transition, closed RCT normally, restored settings and requested Restart.
That restart was not evidence of an RCT crash.

The current framebuffer miniport advertises **one retained boot mode**, with
32-bit pixels, and does not implement palette or hardware mode switching.
Xbox output-format capability does not automatically expose corresponding
Windows/DirectDraw modes. Resolution, pixel format and the mode-switch path all
matter; booting at 640×480 alone has not been shown to fix fullscreen.
Microsoft documents that [DirectDraw mode enumeration](https://learn.microsoft.com/en-us/windows/win32/api/ddraw/nf-ddraw-idirectdraw7-enumdisplaymodes)
returns the modes exposed through the driver. A future bounded API/mode probe
should identify RCT's exact request and result before a driver change.

Sources: [physical run 590](../outputs/rct590/REPORT.md),
[manual save/load run 596](../outputs/rct596/REPORT.md), and
[framebuffer miniport](../src/drivers/video/framebuffer/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c).
