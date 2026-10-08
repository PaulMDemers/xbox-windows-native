# RAM0109 monochrome cursor and restored framebuffer PASS

Independent bounded debugger candidate001 used exactly the ordinary probe122
and unchanged RAM0109 driver. All26cursor-present and26cursor-away snapshots
match independent DIB references and the authored cursor AND/XOR truth table:
5,111,808RGB comparisons, zero mismatches. The26present snapshots cover18,109
cursor pixels;13,579actually differ from background. This establishes visible
composition, including black, white, transparent and inverted regions, nonzero
hotspot and top-left desktop clipping, then correct restoration after drawing.
The bottom-right positions clip at the tested rectangle, not the desktop edge.

The observer pins the compiler's actual pre-move callsite, requires Stage15 and
EAX1000/EDX550, validates bounded reference pointers and captures before executing
the real move. All52runtime DIB references equal their corresponding26cold file
SHA256values. Cursor and restored observations pair by process/thread/index.
433resident byte pins include all11,668relocated display.text bytes. The display
header remains explicitly unreadable(E14); actual loader identity, full resident
code and cold binary hashes are required instead. Two real entry page-fault
deferrals and72foreign-process shared-API hits are preserved. No guest register
or memory forcing, no UI actions. Full breakpoint teardown and resume succeeded.

Normalshutdown1/dashboard return, zero warning/error/application events, complete
allocation325directories/6785files/326directoryclusters with zero errors/orphans,
five structural hives, payload/protected/startup hashes, unchanged96MiBpagefile,
shared-UC mapping and inherited emulator configuration all pass. See
verification.json and candidate001/audit.json. The verifier recalculates every
comparison from preserved private raw captures and cold files.

strict_diagnostic_passed=true; ordinary_qualified=false; physical_qualified=false.
The separate video-cursor-exclusion ordinary run passed independently. Both runs
and all their owned processes are CLOSED. Never relaunch/recollect either case.
No source-driver, cache, physical-console or baseline changes were needed.

Limits: one authored monochrome shape and four repeated positions,26GDIcases.
No color/animated cursor, multimonitor/lifetime race, real mode/boot-video/crash
transition or hardware performance qualification. Earlier four unobserved DDI
callbacks remain unqualified. PhysicalFATX0101/video0093,0088rollback,immutable0.1.0,
qualified128GiBrecovery and prior failures are preserved. Original111-byte
physical damage/restart cause remains unresolved.
