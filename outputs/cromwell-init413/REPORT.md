# 413: original PCI/video initialization observed; screen capture failed

One fresh emulator launch was accepted at 2026-10-16 02:00:10 UTC. Nine stopped
instruction observations include original wrapper/Cromwell entry, C entry,
PCI call/return, video call/return, backdrop return and the USB call before it
executes. All resident checkpoint bytes match the deployed original payload;
all three allocated ELF sections match all288316 payload bytes. Actual video
state reports1280x720. No guest memory/register edits, driver or physical writes.

The planned HMP screendump returned unknown command. The original run remains
FAILED; its source/report are frozen. Separate instruction-review verifies only
completed observations:17 private captures and24 rejected report mutations.
No visual output claim or physical failure reproduction. All18 breakpoint
add/remove operations paired, physical mode0 restored, orderly host exit0.

Cold audit: complete10GB mapping,55 changed bytes, strict whole-disk equality
FALSE. One reserved-sector byte,51 sector8 bytes,three directory creation-field
bytes; writers unknown. Separate full E file inventory:6552 names/hashes exact,
275directories/254directory clusters,zero allocation errors/orphans. QCOW and
EEPROM clean; never-executed preparation002 unchanged,203 frozen inputs exact.
No Windows boot/shutdown or ordinary timing qualification. Never relaunch,
recollect or parent413emu001. User finished recording the physical demo and
explicitly authorized console access again; the baseline remains unchanged.
