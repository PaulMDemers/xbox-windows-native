# Deluxe: PC installation, park rendering and in-session save/load observed

User-supplied RollerCoaster Tycoon Deluxe ISO SHA-256:
`7910b1440239f7026821507180e6dfdbc5a119147baaf77c4e542182c1ad9052`.
A fresh child of the original404 Windows2000 NTFS seed booted with64MiB,
PentiumIII TCG and Cirrus VGA. No network or emulated sound device. Original
ISO mounted read-only. Full installation into C:\RCTDX succeeded. The installer
reported existing DirectX meets requirements; no DirectX replacement selected.
Optional registration skipped. No patches, compatibility shims or binary edits.

The desktop shortcut reached title/menu rendering and animated park background.
ForestFrontiers opened with terrain, trees, entrance, toolbar and objective dialog.
Mousemenus responded. XWN563.SV4 was saved, listed in the load dialog and reloaded
with the park rendered again in the same session. This does not establish load
after Windows reboot,30minute play, construction correctness, sound or FPS.
Game Quit returned to the desktop; Windows Restart ended the VM normally.

Closed-disk checks enumerate483gamefiles/331809236bytes. Saved game290253bytes
has SHA-256 e1f75b800d58b711cabb7c8d5dcaf25d9997766c37700a1f59d0728c77022672.
All five registry hives pass checks; EventLog6006 increases1, only new system
startup/shutdown informational records. Original OS executable/DLL/SYS hashes
remain unchanged. No installed path component exceeds42UTF8bytes, which checks
one FATX constraint only; it is not a qualified Xbox installer or full FATX audit.

Executable hashes/imports and selected install-path registry values are in
installed001.json. Static imports are not an actual graphics-API trace.
Screenshots, media, installed binaries and saves remain private. final001 records
46screens and8frozeninputs. All owned processes closed; no console access.
Hostattempt560 failed before guest boot due to a DrvFS socket and is preserved.
This is exploratory Windows2000 PC compatibility, not Xbox/game acceptance.
