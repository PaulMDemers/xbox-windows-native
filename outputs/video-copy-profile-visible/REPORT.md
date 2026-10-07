# Fixed-driver copy-path baseline

baseline002 is CLOSED and strict PASS: 54 timing cases, 162 full RGB pixel
verification stages, automatic normal restart, dashboard return, zero event
warning/error/application deltas, five structurally parsed hives and unchanged
protected binaries. Full allocation: 324 directories, 6755 files, 325 directory
clusters, zero errors or orphans. Pagefile chain and inherited device policy
remain unchanged. No debugger or UI intervention occurred on this run.

At 768x384 the median milliseconds per iteration were: fill 66, upload 66,
readback 6.82, screen overlap 75, RAM overlap plus upload 69, RAM overlap 0.55.
The screen/RAM-plus-upload ratio across the three geometries was 0.96, 0.83,
1.09. This is not convincing evidence that a shadow display driver would improve
this emulator path. Upload cost remains after avoiding framebuffer reads.

These are three rotated rounds in a functional xemu slot, including GdiFlush,
message pumping and clipping checks. They are not physical bandwidth or window
drag FPS. Earlier physical GDI measurements had a different read/write balance;
do not transfer these emulator timings to the Xbox. No driver or cache changed.
See summary.json for all samples and baseline002/audit.json for strict gates.

The original kit's initialization/visibility failure is retained separately.
This kit's baseline001 failed at the host before Windows launch: xemu could not
open a deep backing path; its run image remained byte-identical to the seed.
baseline002 uses a new short run ID without relocating any backing files.
Its helper raises only its own window and waits for full visibility outside
timed loops. It does not dismiss Welcome or alter startup/device preferences.

The next discriminator is a fresh matched pair using the existing bounded0096
direct reserved-RAM mapping prototype versus0093 aperture mapping. This is an
emulator experiment, not promotion of0096: generic PnP stop/remove consumer
quiescence and restart remain unqualified. GDI self-readback alone cannot prove
scanout correctness for a newly implemented shadow driver.
