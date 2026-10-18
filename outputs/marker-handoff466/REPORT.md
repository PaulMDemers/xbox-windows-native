# 466: both early-entry markers validated in an owned emulator

emu003 passed the scoped diagnostic. The trace observed eight boundaries,
including the actual allocated loader at02000000, original Cromwell entry,
original stack installation and return to026000f5. Both marker records report
two completed SMC transactions, four status reads and no marker error. Full
EFLAGS and the expected general registers were preserved at the two boundaries.
This is emulator/device-model evidence with debugger pauses, not physical LED
confirmation or an intermittent-boot fix.

The integrated XBE is C:/xwn466/build001/default.xbe,537170 bytes,
SHA25674a479078f378b8f02c54d4bd146765a7d860031116f636a3658a6616c2bedf5.
The expanded diagnostic payload is524862 bytes. Source review reconstructs the
exact462 wrapper and original374 payload after removing only the new hooks,
namespace/length changes and owned image tail. Original loader copy/relocation
layout remains1024 bytes,74/80 offsets and224-byte critical span.

Host001 passed57 actual assembled wrapper cases. Stub-host001 passed26 actual
linked post-stack cases, including success and quarantined failures from an
invalid incoming stack. Kernel/file/SMBus/CLI/TSC effects are explicitly modeled.
The separate465 core has32 cases and32 immutable repeated-call checks. Independent
review accepted14 successful host records and rejected101 failed/unexecuted
records plus120 malformed records. The runtime decoders accepted90 complete host
records and rejected35 incomplete/invalid records before launch. Actual emu003
records reject240 mutations/truncations;13 captured memory files were rehashed.

The corrected run removed all breakpoints, restored physical-memory mode and
closed through orderly stop/quit, exit0, without fallback. It stopped at original
Cromwell continuation before Windows. The complete10,000,000,000-byte virtual
mapping was covered;327680 local overlay bytes were compared. There were546
changed bytes, including the diagnostic report and metadata: strict whole-disk
equality remains FALSE. The cold E allocation audit is clean:276 directories,
6554 files,255 directory clusters,zero errors/orphans. QCOW checks and EEPROM
comparison pass. Five hives and the original launcher/FATX/video binaries are
byte-identical to the never-executed seed; this is not a new hive-semantics claim.

Failed emu001 passive FTP staging and emu002 fixed-breakpoint/cleanup handling
are preserved separately. Both owned processes exited0 without fallback; neither
qualifies both markers. Read ERRATA.md before interpreting emu002's inherited
cold-audit stop label. review001's invalid negative fixture is also preserved.

No physical access or physical file change occurred. The installed original
launcher,720p Windows baseline, demo and rollbacks remain untouched. No D3D or
boot reliability qualification is added.
