# Integrated demo

This guide targets the tested E installation on the owned console. It does not
install Windows on an empty disk.

## Start

1. Start at UnleashX with the Razer keyboard unplugged.
2. Select **Windows** from the root menu. If needed, its file explorer can launch
   `E:\Applications\XWNEBoot\default.xbe` directly.
3. Connect the keyboard after Xromwell finishes and Windows appears.
4. Cancel unsupported-device wizards without disabling devices. Close Welcome.

The root **Windows** entry was updated to the E demo on October 14, 2026 UTC.
Reload UnleashX after the update so it reads the new configuration. The prior
menu is backed up at `C:\Dashboard\config.e380.bak`; this was an explicitly
authorized menu-only exception to the dashboard C restriction. The original F
installation and its launcher remain unchanged. Menu boot observation is pending.

## Five-minute demonstration

The current E demo selects720p. Comparison381 produced user-confirmed clean text
and clean full-window dragging; the1080i text/motion issue remains unresolved.

- Move Notepad and Explorer using outline dragging; release the mouse to draw
  the contents at the new location.
- Save a note under `C:\xwndemo372`, close it and reopen it.
- Draw a small Paint image, save as BMP in that folder, close and reopen it.
- Open Calculator, Solitaire, Pinball or an installed screensaver. Running an
  OpenGL application does not establish hardware 3D acceleration.
- Listen for login audio or play an existing local WAV at moderate TV volume.
- Restart normally, then reopen the saved files after the next boot.

Windows C is dashboard E in this installation. Do not use Windows F as scratch:
it is not dashboard F. See [partition mapping](RECOVERY.md).

## Drag controls

The add-on provides `display-settings.exe`, **Outline dragging.cmd**, **Full
window dragging.cmd** and **Display status.cmd** under `C:\xwndemo372`. The first
demo startup applies outline mode once; later user changes are retained.
The preference belongs to the current user and is saved in that profile.

Outline mode moves only a border until mouse release. It does not eliminate the
final repaint or accelerate scrolling, resizing or application drawing. Display
Properties → Effects → “Show window contents while dragging” controls the same
preference. The add-on does not install a display driver.

Full-window dragging is usable in the current720p comparison; outline remains a
reversible preference rather than a requirement.

## Finish

Use Start → Shut Down → Restart to return to UnleashX. The demo has no timed
shutdown or benchmark loop. Report the selected mode, application/action, exact
stop code and whether the system responds if something fails.

Known limits include Ftdisk49, a physical capacity warning, unsupported-device
prompts, software-rendering cost and the Xromwell/Razer boot interaction. This
is a private experimental demo, not a newly certified release.
