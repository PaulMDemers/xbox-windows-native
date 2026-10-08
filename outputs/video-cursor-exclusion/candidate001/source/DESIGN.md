# Visible software cursor exclusion and restoration

Fresh ordinary child; unchanged RAM0109 binary, original shared-UC fixture,
same storage/HAL/network settings and inherited emulator device policy.
Probe122 creates a 32x32 monochrome cursor with hotspot7,11 and all four AND/XOR
truth-table combinations. GetCursorInfo requires exact handle, visible flag and
position before drawing and after moving away. Each of26 actual GDI operations
runs beneath that cursor; positions include desktop top-left clipping, test-area
bottom-right overlap and two interior positions. Reference rendering occurs
while cursor is parked, and must invoke no display callbacks. After drawing,
move cursor away, read back every test pixel and require exact DIB reference,
source immutability, full scanout coherence, exclusive cold reference files,
normal shutdown and unchanged strict event/allocation/hive/protected gates.

GetCursorInfo is state evidence, not independent proof of scanout cursor pixels.
This ordinary test cannot qualify visible mask composition or all cursor shapes.
A separate bounded raw-framebuffer diagnostic is required before claiming those.
No driver changes, direct-hook calls, device-policy changes or physical access.
