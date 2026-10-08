# Probe121 independent emulated framebuffer: strict diagnostic PASS

26 stopped checkpoints compare the independently rendered DIB against emulated
physical framebuffer0x03c00000:2,555,904 RGB pixels, zero mismatches. Each runtime
reference is393216 bytes; its full SHA256 matches the corresponding cold reference
file after normal shutdown. Cursor1000,550 remains outside the384x256 test region.

277resident pins cover actual kernel/probe/API sites and all11668 relocated bytes
of RAM0109 display.text. Probe/kernel/API headers pin normally; display headerE14
is retained as unavailable and compensated by loader identity/full text/cold PE
hash. Two current-entry page faults resolved via actual CPU stepping;73foreign
process shared API hits were recorded and stepped without misattribution.
600second bound, all breakpoints removed, guest resumed and returned to dashboard.

Cold strict workload/integrity/events PASS:26cases/references, normalshutdown1,
allocation325dirs6785files326directoryclusters with no errors/orphans,5 structural
hives, protected/payload/startup hashes, no warning/error/application events.
Same96MiB/1536-cluster pagefile/configuration/shared UC map, exact probe/driver as
ordinary coverage4. No manual UI intervention, physical access or driver change.

ordinary_qualified=false and physical_qualified=false. Independent debugger
results do not establish hardware speed, cursor exclusion, mode/disable/bootvid/
crash ownership or the four unobserved DDI routes. See coverage4 REPORT/NEXT.
All earlier failed observers and unqualified ordinary runs remain preserved.
