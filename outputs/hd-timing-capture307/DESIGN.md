# Timing and kernel-path capture307

New independent standalone capture; no Windows change and no encoder I/O. Preserve305 unresolved readback prerequisite. Capture actual resident kernel pages privately (explicit missing-page bitmap), enabling analysis of the actual4034 stock mode path instead of trusting a legacy-mode SMBus result. This is a prerequisite capture, not a complete encoder reference.

Only23 CRTC timing/stride/interlace indices and3 MMIO config/VPLL/general-control registers added to292. Single-CPU interrupt flags are saved/restored around bounded register reads and selector restore; no log/file/API calls in that interval. No unlock/data-register/timing write; selector is the sole direct register write. Normal stock mode API performs modes, framebuffer is independently checked, recovery640x480 then dashboard.

Primary open driver corroboration: Linux nouveau dispnv04/hw.c state save reads timing CRTC, VPLL and general control; hw.h indexed wrappers. Existing pinned Cromwell and xemu definitions provide exact addresses. This supports this small read set, not arbitrary MMIO side-effect safety. Sources: https://github.com/torvalds/linux/blob/master/drivers/gpu/drm/nouveau/dispnv04/hw.c and hw.h. No palette/status/interrupt registers read.

Fresh unused blank emulator disk first, source/binary/caller/record/full-framebuffer checks and orderly closure/full disk audit. Physical separate one-shot with fixed-file/hive/startup hashes before/after. Private captured kernel never committed. Failed kernel file creation on read-only emulator DVD is recorded, not a successful file capture; debugger independently captures validated kernel pages. Physical requires full file readback. Original reserved-sector strict disk difference remains distinct.
