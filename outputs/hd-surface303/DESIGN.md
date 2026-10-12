# Returned-length surface contract

The candidate requires32bpp, width1..1920, height1..1080, exact width*4 stride, nonzero RAM length at most9MiB, framebuffer length no larger than RAM length, and visible height*stride within framebuffer length. Bounded dimensions make both products fit32bits. Existing complete map-response, non-null pointer and equal framebuffer/video-RAM-base requirements remain common.

The mode is opt-in. Its control compiles the unchanged legacy predicate. Neither branch changes drawing, locking, map lifetime, shadow allocation cleanup, provider ABI or register programming. The actual lifecycle is host-tested with faults; real Windows regression and HD timings remain distinct gates.

Native source comes from the qualified118 Git index tree rather than downloading/updating a toolchain. All recovered source bytes and compiler inputs are pinned. Failed reconstruction and newline transport attempts are retained separately from compiled003. The original source tree is never modified.
