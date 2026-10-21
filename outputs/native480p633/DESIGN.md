#633 explicit native480p boot-profile candidate

Adds mode3 (720x48032bit) from independently validated632 programming facts.
Original modes1/2 remain identical. Adapter accepts only progressive720p/480p,
Conexant, HDTV cable and the matching EEPROM96bit (2/8).19 bounded writes and
all polling/readback/failure limits are retained. No new read-modify-write of
encoder6c or borrowed clock/PCRTC state. The existing values are retained.

XWN_HD_BOOT_MODE defaults to720p; this separate candidate explicitly selects3.
Unsupported compile modes are rejected. Explicit480p unsupported hardware cannot
fall through to legacy initialization: bounded reset request then halt if reset
fails. Successful handoff geometry comes from the same selected profile. The
64MiB/55MiB/9MiB/316160-byte framebuffer contract stays exact. No ordinary launcher
or Windows files are installed by this build. No live Windows switching yet.

Host tests cover both modes and each SMBus failure, busy/timeout, synchronization,
vblank and geometry/pitch/format faults; no success/output exposure after failure.
They are modeled I/O, not actual hardware timing or reset guarantees. Pure output
is independently compared with310 high-mode facts and newly collected632 low facts.

Native emulator preflight: exact compiled XBE in a fresh never-run blank fixture.
Stop at the real wrapper return, verify text/state/vmode/readable timing and
framebuffer address, then close. No guest register/memory patch and no Windows
launch. This is only initialization proof; no disk or runtime promotion. Preserve
all failed gates. Full fresh Windows boot/drawing/input/restart qualification and
watched physical trial remain required before mode selection is offered.
