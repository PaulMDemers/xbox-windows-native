# First HD controller attempt failed; sources preserved

Native build001 compiled against unchanged pinned nxdk prebuilt libraries and
passed binary/checkpoint review. The original independent host compiler attempt
failed without diagnostic text. Host002 compiled after setting a process-local
compiler PATH, then failed because Windows stdout expanded LF bytes to CRLF.
Host003 uses binary stdout; the actual unchanged guest pixel helper and independent
host oracle match13,209,600 bytes, with12 changed-pixel negative controls.
Private sources/binaries/logs remain E:/xwn289/host001..003. Preparation initially
continued after the host compile error; a separate prelaunch review required the
passing host003 oracle and unchanged frozen dependencies BEFORE any launch.

Only the NEW private EEPROM video flags/user checksum changed; shared emulator
EEPROM and physical EEPROM are untouched. The generator's checksum and reviewed
EEPROM field structure are recorded in DESIGN.md/eeprom001.json. Original bytes
are preserved. This is explicit fixture configuration, not a physical capability.

Single emu001 launch verified720p allocation/scanout/all-page translation and
3,686,400 exact independent framebuffer bytes. Then the original hardware
breakpoint retriggered immediately because the controller had not stepped past
it. The original failure is preserved, not called a guest mode failure or1080i
pass. All breakpoints removed, physical mode restored, bounded resume and orderly
host exit0. No guest terminal/reboot claim. Full cold audit: QCOW clean, all
source/dependency pins and EEPROM unchanged. Strict full-disk equality FALSE:
one reserved-sector byte; filesystem bytes inherited unchanged across the full
8GiB map and65,536 overlay bytes. No gate waived.

290 is a separate corrected controller/fresh runtime using the same native binary.
Never relaunch, recollect or parent from289emu001. No physical launch, Windows
driver/bootloader change, release/tag or GPU ownership claim.
