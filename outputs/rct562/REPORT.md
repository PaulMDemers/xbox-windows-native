# Later Atari disc: PC installation, park rendering and save/reload observed

User-supplied `Rollercoaster Tycoon.iso`, SHA-256
`e5aa622a680f7a61383d3456e8ee3cd16c3e31f5955a9035b799b3fe1f941539`,
was installed fully into `C:\RCTLATER` on a fresh original404 Windows 2000
NTFS child. The PC control used 64 MiB, Pentium III TCG and Cirrus VGA, with
no network or emulated sound device. The original ISO was read-only.
Existing DirectX was accepted; optional registration was skipped.

At 640 by 480 the Atari registration dialog's Close control was below the
visible area. Windows was changed to 800 by 600, 16-bit color: the first apply
timed out and reverted; the second was confirmed. Registration was then
dismissed with Never Register. The game launched once from its desktop shortcut
and switched to 640 by 480. No executable patch or compatibility shim was used.

The title menu and Forest Frontiers rendered. Mouse menus responded. Save Game
created `XWN562.SV4`; a screenshot confirmed return to the park before Load Game
was selected. The save appeared in the load dialog and reopened with the park
rendered again. About reports version 1.08.187. Quit Game returned to Windows;
the observed Windows Restart selection ended the VM normally without host quit
or deadline intervention.

Closed-disk checks found 113 game files, 161271082 bytes, including the
290328-byte save. No installed path component exceeded 42 UTF-8 bytes. This is
one FATX constraint only, not a complete installation or allocation audit.
All five registry hives passed, EventLog6006 increased by one, and protected OS
EXE/DLL/SYS hashes remained unchanged. The original disc and seed remained exact.
`final001.json` records 54 private screenshots and eight archived source inputs.

Although this edition displays the same version as Hasbro561, its installed
`rct.exe` is 3166720 bytes with SHA-256
`48401f91c8363106a6bc3b7e98f17aaac7e2069a995b4e7052fb6631ae191848`.
Hasbro561's executable is 6009344 bytes with a different hash; the discs are not
interchangeable controls. No attribution for that binary difference is made.

All owned processes are closed. No physical console access occurred. Audio,
frame rate, extended play, construction, across-reboot load, Xbox compatibility
and GPU acceleration remain unqualified. Static imports are not an API trace.
