# Display mode switching on the development Xbox

The current Windows package boots at1280x72032bit on the qualified Conexant,
64MiB development console. It does not yet offer live resolution changes.
[The miniport](../src/drivers/video/framebuffer/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c)
reads the boot-established scanout geometry and pitch, reports one mode, and
accepts only mode index0. Merely adding640x480 to its enumeration would advertise
a mode that the driver cannot actually set.

The current work starts with a second, independently qualified480p boot profile.
That makes it possible to validate a lower-resolution desktop and the complete
loader-to-Windows framebuffer handoff before changing resolution during a live
Windows session. The normal720p launcher and recovery package stay intact.

## Initial mode-transition diagnostic

[Diagnostic631](../outputs/mode-switch631/REPORT.md) uses the stock Xbox kernel's
video API, through the existing nxdk, to request720x480 →1280x720 →720x480 at
32bit60Hz. This is a standalone application, not a Windows driver. It requires
an HDTV AV pack, enabled480p/720p flags, enumerated modes and64MiB. It does not
force cable detection or modify the EEPROM.

The720-wide low mode is intentional. Earlier stock640-wide tests exposed
720-wide scanout timing with a640-wide framebuffer pitch. The present Windows
handoff reads the hardware width and requires a matching four-byte pixel pitch;
we must establish a consistent contract rather than infer one from the signal's
480p label. A future640-wide mode may be possible, but it needs its own viewport,
pitch and timing handling.

The first emulator run completed both transitions and restored the low-mode
timing values. Its full framebuffer bytes matched the independent oracle at all
three stages. This does not establish physical picture quality, a480p Windows
boot, or live Windows mode switching. See the report for the retained disk-audit
failure and the limits of the read-only optical launch.

## Remaining implementation and qualification

1. Complete a watched stock-API transition on the original development console,
   with exact staged bytes, a fresh output path and protected-file checks. Record
   picture stability and automatic dashboard return separately from API success.
2. Establish a complete480p programming sequence from reviewed source and actual
   hardware evidence. The old legacy encoder path ignores write statuses and
   uses the previously unreliable6c read-modify-write; it is not an acceptable
   shortcut. Timing snapshots alone are not a complete programming recipe.
3. Add an explicit lower-resolution boot profile with bounded programming and
   failure handling. Keep the64MiB/55MiB framebuffer/9MiB reservation contract
   consistent across Xromwell, FreeLoader, bootvid and miniport. Validate geometry,
   row pitch, pixel format, hidden storage and bounds before a Windows launch.
4. Qualify a480p Windows desktop, drawing, input, file persistence and normal
   restart, followed by the unchanged720p path. Only then expose a supported
   boot-mode selector or automatic selection policy.
5. Implement live Windows switching as a separate driver change: mode enumeration
   and validation, hardware programming, display/surface teardown and recreation,
   failed-change rollback, and DirectDraw/fullscreen restore. Test repeated
   low/high transitions, application exit and return to the desktop.

Adapter detection means the Xbox's AV-pack classification plus encoder identity
and enabled video flags. It is not identification of the HDMI adapter's retail
brand or a reliable reading of the attached display's supported HDMI modes.
Keep an explicit override and known-good recovery path when automatic selection
is introduced. Focus/Xcalibur and additional-console qualification follow the
[compatibility matrix](console-compatibility.md); this work targets the existing
supported revision first. The separate1080i investigation remains tabled.
