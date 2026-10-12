# 1080i before 0.2.0

User priority supersedes the previous cache-disposal implementation queue.
Automation remains paused; the user authorized this new interactive work.

1. Prepare a bounded standalone 720p/1080i diagnostic using the owned Xbox
   kernel's supported mode API. It must refuse the current standard AV pack,
   use independent pixel checks, retain mode registers and return to a known
   supported low-resolution mode. Emulator HDTV capabilities are a private
   fixture setting, never a change to the physical EEPROM or a GPU grant.
2. Integrate explicit boot-time HD selection into an isolated Windows launcher
   and consumers. The existing Cromwell path hardcodes 480p even though Conexant
   and Focus encoder functions contain HD cases; Xcalibur's helper always emits
   480p. Correct encoder and CRTC/field timing must be established together.
3. Coordinate a framebuffer layout across launcher, multiboot map, FreeLdr,
   bootvid/shared provider, miniport and display. Full 1080x1920x4 needs 8,294,400
   bytes. Bootvid also needs 316,160 bytes for its indexed 640x494 backing area:
   8 MiB is insufficient even before other reservations. Simply growing the
   top-RAM buffer overlaps Cromwell code at 0x03A00000 and stack at 0x03BFFFFC.
   Do not clear/map such a layout or silently lower color depth. Audit all live
   loader areas and preserve the original recovery launch path.
4. First validate the new handoff and exact pixels in fresh emulator children;
   then ask for the HD-capable connection/display before physical mode trials.
   GPU acceleration, full backend retirement, and runtime Windows mode switching
   remain separate. Tag 0.2.0 only after the agreed 1080i milestone is stable.

Never relaunch/recollect physical001 or emu001. Collection failed once before
FTP returned (connection refused, no collection began); the later collection
completed. Nothing was relaunched. Full-disk equality failure remains recorded.
