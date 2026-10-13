# Contributing

Use isolated checkouts and record source, binary and tool hashes. Preserve failed
attempts and use fresh IDs; never parent a fresh emulator test from an executed
disk. Coordinate hardware access and shared build/emulator resources.

Bug reports should include console revision/encoder, cable, boot profile,
component versions, application/action, exact stop code, restart method and
whether it happened on hardware or xemu. Remove credentials, product keys,
EEPROM contents and personal files.

Explain behavior, mechanism, validation and limits. Display changes require
independent pixel/guard checks and actual callback coverage. Storage changes
require cold allocation/content/hive checks and shutdown evidence. Emulator
timings do not establish hardware performance.

Do not suppress events or disable devices merely to pass a test. Retain license
headers and identify derived code. Public patches must not embed owned Windows,
firmware, dashboard or user data.
