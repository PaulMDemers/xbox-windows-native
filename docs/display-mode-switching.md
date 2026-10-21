# Display mode switching on the development Xbox

The current Windows package boots at1280x72032bit on the qualified Conexant,
64MiB development console. It does not yet offer live resolution changes.
[The miniport](../src/drivers/video/framebuffer/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c)
reads the boot-established scanout geometry and pitch, reports one mode, and
accepts only mode index0. Merely adding640x480 to its enumeration would advertise
a mode that the driver cannot actually set.

The current work is a separate480p boot profile, which still needs Windows qualification.
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

The original development console subsequently passed the same watched sequence.
The user reported stable output and automatic dashboard return; the collected
log passed independent pixel/geometry checks, with identical first/final low-mode
timing. Ten protected Windows/launcher/startup files were unchanged. See
[physical closure](../outputs/mode-switch631/physical-final001.json). This completes
the standalone hardware prerequisite; native480p Windows boot remains untested.

## Remaining implementation and qualification

1. Completed: watched stock-API transition on the original development console,
   exact staged-byte checks, durable result log and protected-file comparison.
   User-reported picture stability is recorded separately from API/CRC success.
2. Completed source preparation: [632](../outputs/mode-facts632/REPORT.md)
   independently verified the missing480p programming facts on the original
   console, including exact setter identity and comparison with known profiles.
3. Implemented as an experimental separate loader:
   [633](../outputs/native480p633/REPORT.md) selects720x48032bit while retaining
   bounded encoder writes and the existing memory contract. Host tests and native
   initialization against a matched emulator control pass. Full physical timing
   equality and a480p Windows boot remain unqualified. The ordinary720p package
   is unchanged. Historical feature/function names retain720p for compatibility;
   the candidate explicitly builds with `XWN_HD_BOOT_MODE=3`. It is not yet an
   end-user mode selector or a supported package.
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
