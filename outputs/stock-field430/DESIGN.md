# Stock video API field comparison

Use the same byte-identical428 pattern helper through pinned nxdk XVideoSetMode,
without Windows or Xromwell. Enumerate actual supported32bpp60Hz modes and refuse
missing HDTV detection or720p/1080i modes. No EEPROM flags or custom video-register
writes are made. The stock SDK/kernel video API itself programs the display.

Each mode lasts four approximately ten-second phases: static, parity shift,
moving rectangle and static. Blue top bar identifies720p; orange identifies1080i.
The actual framebuffer allocation is queried and must contain width*height*4.
Paint writes only that allocation. Capture uses volatile CPU reads, compares
RGB bytes to the pattern, and writes four separate CREATE_NEW files per mode.
No vblank synchronization or double buffering is added, so ordinary tearing can
occur during motion. This is not Windows USER movement and contains no text.

Records include actual dimensions, allocation/physical address, scanout and16
read-only video registers, phase/frame/time, mismatch count and completion.
Synchronous stock file/video calls have no independent cancellation guarantee;
the phase loop is time/frame bounded. The firmware restart request is after
closing the output, including failure paths. FTP return alone does not prove it
ran. One immutable launch receipt per case; never retry a sent case.

Build002 used E: DOS paths, but linked nxdk automount_d_drive only guarantees D:
for the XBE's launch directory. physical001 returned no result. Build003 changes
only the two output-path strings and comment to use D:. This stock-Xbox alias
is not a host disk or Windows drive. The controller launches the exact owned XBE
under dashboard E:/Applications/XWNField430c, checks absent results, and does not
change Windows startup or launcher. No dashboard C reads/writes are requested.

The actual paint function passes23,961,632 ASan/UBSan pixel/guard checks in a host
buffer at both modes and extreme positions. Flush is modeled. The independent
record parser rejects64 malformed modeled records. Same pattern bytes had the
separate428 independent Python oracle. This is not an emulator run; physical
execution and visual observations must be reported separately.
