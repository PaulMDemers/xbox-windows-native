# Standalone HD API and memory diagnostic

Emulator-only authorization for this kit. No physical runner or deployment.
The unchanged owned Xbox kernel sets720p,1080i,then640x480 using pinned nxdk
XVideoSetMode. Cable and all three capability flags must be present. Native
CPU-written patterns have an independently generated host oracle. Full logical
framebuffer readback, actual allocation/physical address, scanout and16 FP timing
registers are captured at each checkpoint. This tests the stock-kernel path,
NOT the Windows/Cromwell handoff or physical interlaced output.

The SDK allocation assert and AvSetDisplayMode loop have no individual timeout.
Owned host controller/runner watchdogs bound an emulator hang. No physical claim
of automatic recovery follows. No PBKit reset, EEPROM guest write, firmware
channel/object borrowing, Windows launch or renderer observer/release operation.

Private EEPROM child only: set720p/1080i/480p flags in user video field0x94,
recompute user checksum0x60 over0x64..0xbf using pinned xemu generator algorithm.
Preserve original byte file and allow changes only to that field/checksum.
Primary field reference:
https://github.com/feudalnate/Original-Xbox-Data-Structures/blob/master/EEPROM/README.md
The physical EEPROM/adapter/settings remain untouched.
