# Test762 staged: later CR02 write

Source-only760 extension after native761 CLOSED PASS. The original mode sequence
writes CR02 again after CR01 and before CR17enable. This probe captures the
current CR02 byte, checks it against the earlier readback, writes59, checks six
neighbors and reverses its own write first before older recovery operations.
No display-enable, pitch, vertical, PLL or encoder steps are added.

This is a same-value write: expected59->59->59. Readback cannot distinguish a
dropped forward write or dropped same-value undo. Two explicit model controls
pass with identical raw results; a wrong-write-plus-dropped-undo control fails
and keeps output disabled. Matching readback does not establish a value change.
The earlier first CR02 operation retains its separate full own-value restoration.

Fresh209 actualCOFF execution cases,2353layout cases,10 actual clock-gate cases,
independent schema mutation/source/order checks and PE/XBE linked-byte reviews
passed. The188-word752-byte result would end53f0 at future native offset5100;
a native counterpart still needs fresh bounds/CPU/relocation/optical validation.
Clock remains3375000 with highword0. Exact frozen source and Git index match.
The unique E/Applications/XWNMode762 package was staged and read back exactly.
No startup hook or dashboardC access, no nativehandoff or Windows launch.
No physical result yet. No complete mode-switch/Windows1.6 qualification.
Preserve760model001 and all earlier failures; no closed runtime reused.
