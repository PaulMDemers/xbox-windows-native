#635 read-only Windows mode queries

Use the unchanged633 native480p launcher and a fresh child of immutable466.
The complete634 probe remains failed: primary surface Lock is unsupported.
635 replaces that probe operation with GetSurfaceDesc, requiring explicit
DDSD_WIDTH/HEIGHT/PITCH/PIXELFORMAT flags and720x480x32/2880 geometry.
It also attempts the existing QUERY_CURRENT_MODE ioctl on the enumerated
DISPLAY device with GENERIC_READ. A denied handle/query is recorded, never
worked around by patching permissions or a driver. A successful query must
return the correct80-byte descriptor and geometry. No mode-set IOCTL is used.
GDI oracle, normal restart and cold integrity requirements remain unchanged.
No primary-lock capability or complete634 pass may be inferred from635.

Unattended login is not claimed: the recorded installation login is submitted
once under the UI lease only after viewing the owned logon screen. Secret
values stay in private405 configuration, which was used successfully in634.
HMP read-only framebuffer captures replace the unsupported screenshot command;
geometry interpretation alone is not a replacement for guest/pixel evidence.
Host bound remains600seconds and192MiB projected allowance. No physical action.
