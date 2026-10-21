# Display mode switching on the development Xbox

The current Windows package boots at1280x72032bit on the qualified Conexant,
64MiB development console. It does not yet offer live resolution changes.
[The miniport](../src/drivers/video/framebuffer/win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c)
reads the boot-established scanout geometry and pitch, reports one mode, and
accepts only mode index0. Merely adding640x480 to its enumeration would advertise
a mode that the driver cannot actually set.

The separate 480p boot profile has now passed a watched Windows desktop and
drawing test on the original development console. This validates a lower-mode
boot handoff; live Windows resolution changes remain unimplemented. The normal
720p launcher and recovery package stay intact.

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
the standalone hardware prerequisite; the subsequent Windows result is below.

## Watched Windows 480p result

[Trial 638](../outputs/windows480p638/REPORT.md) reached the Windows desktop on
our original console. The user saw the brief test pattern and automatic restart.
Windows reported 720x480x32 at 60Hz; the DirectDraw primary descriptor reported a
2880-byte stride. Full-window GDI upload/readback and overlapping copies in both
directions returned zero pixel mismatches. The result survived restart, one new
EventLog6006 confirmed normal shutdown, protected files matched and five hives
parsed. The temporary startup hook was removed on dashboard return.

The earlier 637 attempt returned before producing a probe result; it remains a
failure. Trial 638 was an explicitly requested watched repeat without a reported power
cycle. This pair does not establish a cause for boot intermittency. Ftdisk 49
remains, and the physical audit covers selected files/hives rather than a full
FATX allocation scan. Primary-surface Lock remains unsupported as observed in 634;
the stride result comes from GetSurfaceDesc. No live mode switch, 640-wide mode,
additional-console qualification or automatic selection is implied.

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
   equality remains unqualified. A watched Windows boot subsequently passed the
   scope described above. The ordinary720p package is unchanged. Historical
   feature/function names retain720p for compatibility;
   the candidate explicitly builds with `XWN_HD_BOOT_MODE=3`. It is not yet an
   end-user mode selector or a supported package.
4. Watched physical interaction now passes on the original console:
   [642](../outputs/windows480p642/REPORT.md) confirmed normal mouse dragging,
   Notepad typing/save/reopen, exact postrestart file bytes and normal shutdown
   at720x480x32/60Hz. [643](../outputs/windows720p643/REPORT.md) then returned
   through the unchanged720p launcher; the user reopened the same saved text,
   and independent file/hive/event checks passed after another normal restart.
   Ftdisk49 and boot intermittency remain; the failed640 attempt is preserved.
   This completes the interaction prerequisite, not a boot-reliability claim.
   Next implement and validate an explicit boot-mode selector with720p recovery,
   followed by a conservative automatic selection policy.
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
