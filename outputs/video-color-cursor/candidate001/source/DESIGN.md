# Color cursor replacement and hide/show through NT5 user32

Fresh ordinary child with unchanged RAM0109 and inherited shared-UC fixture.
Probe123 creates two32x32top-down24bpp color cursors using CreateIconIndirect,
explicit1bpp masks and hotspots7,11/15,3. Colors vary with x/y/shape; transparent
vertical mask stripes have zero color bytes. Source bitmaps are unselected before
CreateIconIndirect, then deleted after the API copies them. This tests their
actual lifetime independently of the resulting cursor objects.

Each of26real GDI operations draws beneath shape n%2, checks visible state,
hides via SetCursor(NULL), checks absence, shows the other shape in the same
location, checks replacement, then moves away and requires exact restored DIB
readback. GetCursorInfo flags/handle/position and GetCursorPos are checked.
Three passive exported markers enable a separate same-binary raw framebuffer
oracle; they do not invoke hooks or mutate driver state. Cold reference files,
normal shutdown, full allocation/hives/protected bytes/event gates unchanged.

No driver changes, new device policy, physical access or cache/mode mutation.
Limits: no animated/alpha cursors, ShowCursor count API or lifetime races.
API ownership reference:
https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-createiconindirect
