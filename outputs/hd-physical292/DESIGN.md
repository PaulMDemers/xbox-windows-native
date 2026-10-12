# Bounded standalone mode diagnostic

A fresh exclusive application-local log records each stock-kernel API mode transition, contiguous allocation, scanout, independent CRC and 16 FP registers. Every log write is flushed. Guest pauses are 10 seconds in 720p, 25 seconds in 1080 and five seconds in fallback, then completion and a ten-second reboot delay. Kernel mode internals are not independently time-bounded; no unconditional physical recovery claim is made. Emulator control has an owned outer watchdog and orderly teardown.

Patterns use an independent byte oracle: one-pixel white outer border, interior B=(x xor y), G=y, R=x, A=255. The physical decoder requires exact stage order, sizes, CRC, all register entries, zero mismatches, completion and log_ok. Logging is unavailable on emulator read-only optical D:; that fact is separate from the physical log requirement.

No EEPROM edits, GPU channel ownership, pbkit reset, Windows startup change or installed driver change. The current physical baseline remains the rollback.
