# Full marker refusal capture validated

Exact466 child build001 adds a version2 192-byte refusal file containing the
complete first-marker state. The marker source, predicates and payload are
unchanged. Reversing the explicit capture edits reconstructs the original source.
XBE537170 bytes SHA256184c08709673d0b2a9128579dc248782b2b6e9431b816e43c0cb0ee860dd46bc.

Actual assembled-wrapper host execution passed85 cases. Kernel,port and timestamp
interfaces are modeled.73 complete refusal records decoded;243 malformed records
rejected. The snapshot survives later live-record mutation; file failures never
retry or hand off. Complete bytes alone do not certify final flush/close.

Fresh emu001 reached both markers, the original loader, stack install and original
continuation. Fresh emu002 first passed the natural marker, then explicitly wrote
a synthetic failure record and entry registers with the debugger. Its actual
refusal memory and192-byte cold file matched. That intervention validates the
serialization path only; it does not reproduce physical status or boot failure.
Both stopped before Windows, removed every breakpoint, restored physical mode
and exited0 through orderly host stop/quit without fallback killing.

Cold complete10GB mappings and local extents were compared. Both allocation
audits found276 directories/255 directory clusters and zero errors/orphans;
6554 files in001 and6555 in002. Five hives and three baseline binaries were
byte-identical. Disk equality remains FALSE:545/816 changed bytes, including
intentional reports/metadata and reserved-sector change. EEPROM/seed unchanged.
514 actual-record negative controls passed. Private captures remain C:/xwn468.

Preserved failures: decoder001 overconstrained last status at a clock/phase
transition; corrected002 is separate. Cold002 failed Windows-path conversion
after a clean scan; cold003 corrected only lookup syntax, without guest rerun.
Final review001 used an invalid negative (nonzero handle changed to nonzero);
review002 tests missing handle and retains the original failed review.

Physical use is recorded independently in physical-status469. No old runtime was
reused as a parent, restarted or recollected. No SDK/driver/shared-source change.
