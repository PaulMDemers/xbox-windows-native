# 850 held 633 stage-marker diagnostic

This is a separate diagnostic of the pinned 633 480p source, conditional on a successful 849 prerequisite report and a separately observed 848 failure. It is not a functional package replacement and has not been launched. The XBE SHA-256 is `faa4bdae01125bb4e769d4b83d8e055e4be8623b6eec522c09a18dd2727ed46d`. Changes are in `marker850-002.patch`; the initial 001 build is retained as a source/comment provenance record.

A watched observer should record the full front-panel sequence and the screen, without assuming a missing light means a specific stage. Each successful marker holds its SMC LED pattern for approximately three seconds before continuing. Hardware and timer failures prevent a guaranteed time bound. Pattern masks use the established SMC red high nibble / green low nibble convention:

| SMC pattern | Intended observation | Meaning when actually observed |
| --- | --- | --- |
| 0x05 | intermittent green | Native code passed PCI, RAM and EEPROM initialization; not the earliest XBE entry. |
| 0xf0 | solid red | Entered native 480p guard wrapper. |
| 0x0f | solid green | Adapter guard passed; display transaction about to start. |
| 0xff | solid amber | Display transaction returned success. |
| 0xa5 | alternating red/green | Immediately before calling the E loader dispatch; not proof the loader started. |
| 0x50 | intermittent red, held | Adapter guard refused. |
| 0xf5 | red with intermittent green, held | Display transaction failed. |

A held failure replaces the original quick reset and requires a manual power cycle. Other existing code changes LEDs between markers; after dispatch, loader or Windows may change them again. If an LED write fails, the previous pattern can remain, so a pattern alone cannot establish a terminal hold unless it is sustained and the sequence is observed; even that is not proof against an unrelated hang. Marker transactions and their delays alter timing and can change behavior. No EEPROM, configuration, boot files, or other persistent state are written by marker code. The existing FATX loader and Windows can write after dispatch; no read-only guarantee extends beyond it.

The existing 633 modeled adapter suite passed 235,552 assertions against the instrumented source with the marker stubbed. The actual marker function passed 768 modeled cases across all masks and first/second SMBus write failure. Tests do not model hardware SMC, timer accuracy, real encoder, full launcher, or Windows. Failure comments in the first build were corrected in build002; XBE bytes remain identical.
