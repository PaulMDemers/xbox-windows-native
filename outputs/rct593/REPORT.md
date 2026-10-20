# RCT593: bounded save observation passed on fresh PC

The helper submitted Save once, then observed five equal full-file SHA1 reads.
The first successful complete read finished1484ms after observation started;
five equal reads spanned4390ms and the whole wait took6203ms. These include
read/hash/logging costs; they are not isolated save latency or game performance.
The290244byte XWN593.SV4 recovered after normal restart has the same SHA1,
af6dbb5a131aa2ec79f5574bb3a9e99ce90985fa. SHA256 is
ca9a26c940a6dfc8dc5ba53cf8717eb4eb7b247140aa636a0afd29b9bbf5947e.

Private before/after images show paused Forest Frontiers with the save dialog
gone. The full helper sequence passed, game exited0 without forced termination,
registry subtree and desktop were restored, and EventLog6006 increased by1.
Cold audit hashed7000files/315directories, checked five system hives and protected
OS binaries. This is not an independent NTFS allocation ownership audit.
The64MiB PentiumIII PC fixture used an immutable404 seed and installed502 verified
retail files. Both virtual CDs were ejected before helper launch. No old runtime
was reopened and no physical Xbox was accessed by593. The fixture is now closed.

The actual C wait policy passed11 host cases. Build001 failed because the local
4096byte array required an unavailable stack probe; build002 uses a static array.
The failed source/log remain private. A mistyped Display Properties command during
busy Windows startup was preserved, then corrected after verifying the Run text.
Save-review001 wrongly expected bottom-up BMP; save-review002 checks the exact
top-down header, lengths and pixel layout. The original failed review is retained.
A final screenshot request hit the already-closed runtime guard after normal exit.

Storage recovery archived exact historical leaf disks and a retained raw335
conversion into verified zstd files on E before removing their originals. All
paths/hashes are in archive003.json; no backing references were moved. Earlier
compression001 completed but failed the reserve goal, with an unexplained C-space
drop; compression002 compressed no files. Both failures are retained. The archive
operation restored C above22GiB and E above27GiB before admitting the new fixture.

This qualifies the corrected save observation helper on PC. It does not establish
Xbox save behavior, reload, acceleration or FPS. Next: matched physical594 using
the exact binary, retaining the prior physical592 save under its existing name.
