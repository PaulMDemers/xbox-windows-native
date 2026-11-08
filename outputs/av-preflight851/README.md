# 851 read-only AV preflight

The 849 source is reproduced exactly except for the unique `xwn-av851` report namespace and encoder SMBus address `0x8a`, the HAL 8-bit form of native 633's 7-bit `0x45`. An encoder response alone does not identify the encoder or prove 633's native guard or display transaction succeeded. The 849 `0xe0` read was at a different address and its failure does not establish a 633 prerequisite failure.

Reports use exclusive creation at `E:/xwn-av851-NN.json`, flush and exact readback before requesting firmware reboot. No EEPROM/settings writes, video mode programming or boot-chain launch occurs. Kernel SMBus, filesystem and firmware calls have no application-enforced timeout. The host tests cover 8192 predicate cases and verify exact source delta and address; hardware was not accessed for this build. Full scope and interpretation follow the 849 diagnostic, with the corrected address.
