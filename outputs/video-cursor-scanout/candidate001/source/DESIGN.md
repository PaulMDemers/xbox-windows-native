# Independent cursor and restored-background framebuffer oracle

Same exact probe122 and RAM0109 binary as ordinary cursor-exclusion. New immutable
child only. Runtime-pin compiler call site immediately before cursor moves away;
require actual EAX1000/EDX550, Stage15, bounded reference pointer and exact PE.
No registers/memory are forced. Capture raw physical framebuffer plus virtual DIB
reference after GDI draw while cursor is still present, and again at existing
exported marker after cursor leaves. Independently apply all four AND/XOR states,
hotspot7,11 and clipping; require exact RGB over384x256 in each of52 captures.
Runtime DIBs must equal all cold saved references. Require paired process/thread,
all display.text pins, full breakpoint teardown and unchanged strict cold gates.
Read current actual attempt records before any launch or collection; one-shot.
This is debugger evidence, not ordinary/hardware qualification or color cursor
coverage. Current Microsoft pointer exclusion docs describe modern behavior;
actual NT5 behavior must be observed, not inferred from that obsolescence note.
Mask reference: https://learn.microsoft.com/en-us/windows/win32/menurc/using-cursors
