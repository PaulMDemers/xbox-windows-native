# Existing-console mode switching: first prerequisite

The user's current priority is mode switching on the supported development
Xbox. Windows currently inherits one boot mode and advertises one miniport mode.
This kit is the stock-kernel characterization prerequisite for a separate 480p
Windows boot profile; it does not implement live Windows mode changes.

New standalone application631 requests 720x480,1280x720,720x480 at32bit60Hz
through the pinned nxdk XVideoSetMode API. It requires a detected HDTV pack,
both480p/720p enable bits, enumerated dimensions and64MiB. The pinned nxdk mode
enumerator excludes interlaced480 entries when480p is enabled; no pack override
or EEPROM modification is performed. Refusals are results, not retries.

At each stage: write an original border/gradient pattern, flush and compare every
pixel, compute CRC, record allocation and physical scanout, read23 documented
CRTC timing indices, three config/PLL words and16 FP timing words. Restore the
CRTC index and saved interrupt flags exactly. Require width/height minus one,
pitch4*width, format3 and noninterlaced CRTC39=ff. Capture precedes geometry
refusal so an unexpected value is retained. Wait10seconds per successful stage,
then request dashboard reboot after a final10seconds. SDK mode calls themselves
can hang: this is bounded application work, not a hardware watchdog guarantee.

No kernel/firmware memory capture, encoder reads or writes by application code,
pending-bit clear, Windows startup hook, Windows boot, driver patch or normal
launcher replacement. The kernel video API necessarily programs display hardware.
The former legacy480p Conexant path's unchecked encoder6c read-modify-write is
not reused. Stock640-wide output previously had720-wide scanout timing; this
probe explicitly tests720-wide allocation/pitch instead of guessing.

Build with the shared nxdk under the build lease. Private artifacts under
C:/xwn631 only, with projected20GiB reserve. Emulator uses a fresh copy of the
owned unused blank disk, private HD-enabled EEPROM and stock xemu; no executed
runtime parent. Pin actual XBE/header/text/checkpoint/callers, translate every
framebuffer page, compare all pixels to an independent host oracle. Clean up
breakpoints, physical-memory mode and owned processes. Record disk deltas and
EEPROM identity independently; any failed audit remains failed and requires
review before physical admission. Emulator output does not qualify a cable,
encoder or Windows handoff.

Physical launch is not yet admitted. Original-console availability is pending.
When admitted, use a new owned E application folder, exact staged bytes and one
SITE request with20second reply bound. Never repeat an uncertain launch. Record
actual user observation and automatic dashboard return separately from API/CRC
results. Preserve original720p launcher, startup and protected files.

Next native work requires independently justified480p programming data and a
coordinated framebuffer contract through Xromwell, FreeLoader, bootvid and
miniport. Do not treat these readbacks as a complete register programming recipe.
