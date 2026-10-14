# FATX390 physical validation

The candidate failed physical validation. One Windows launch was accepted at
2026-10-14 18:21:49UTC. The user reported a blank console window, one hardware
wizard and unavailable input, then rebooted to UnleashX. Return was observed
at18:34:30UTC. The exact reason file work did not complete remains unknown.

The test changes only the E installation's FATX driver and temporary startup.
Video303, audio004 and E720p374 remain unchanged. Original0101 is preserved and
must be restored during collection, after normal startup is restored first.
Dashboard C and the original F Windows/launcher are untouched.

Before launch, the read-only E allocation scan found661 directories,7756 files,
678 directory clusters and zero errors/orphans. All62 frozen inputs matched.
The actual bounded FTP store/rollback code passed eight modeled transfer cases,
one corrupt-readback refusal and six path/payload/case refusals. These are host
fault tests, not physical rollback results.

The workload runs the original six CMD file operations, native386 exact-name
enumeration/copy/rename/readback, then the established setup/audio/GDI supervisor.
It requires exact cold BMP/text bytes and absent intermediate files, not just
successful API return codes. The independent post-return scan, hive/binary
checks, event delta and normal shutdown determine the outcome.

The emulator precursor393 passed CMD/API/audio/GDI and cold integrity; the
original0101 control389 returned duplicate exact-name results. The390 source
fix adjusts cached non-root FATX indices into logical enumeration space; it
does not change allocation or file-data write paths. Physical validation is
still required. The prior387 early-return cause remains unknown.

The known Ftdisk49 warning must remain a strict failure if observed. A scoped
demo PASS does not imply a strict release, full disk-content comparison,
crash-dump qualification, 1080i fix or audible stereo confirmation.

## Closed result

CMD COPY_BMP and MOVE_BMP returned0. REOPEN_BMP began but never logged return.
Saved.bmp is exactly6,220,854 expected bytes; reopened.bmp has a correct
3,866,624-byte prefix and2,354,230 zero bytes afterward. This is consistent with
an unfinished copy, not evidence identifying the blocked operation. The native
probe and setup/audio/GDI supervisor never started. No normal shutdown event
was recorded. The visible wizard was not handled because the helper was later
in the sequence. This ordering issue does not establish the cause of file IO
progress stopping.

Collection restored normal startup first and original0101 with exact readback.
After-scan:663 directories,7773 files,680 directory clusters,zero errors/orphans.
Five structural hives, selected device policy, protected binaries and F rollback
passed. Final-state readback closed18:38:25UTC. The sole warning/error delta was
Ftdisk49, retained. Integrity scope PASS; workload, persistence and strict gates
FAIL. This is not a full disk-content audit.

Cold registry evidence selects ControlSet001 XwnFatx Start0 with ImagePath
system32\drivers\xwnfatx.sys; stock Fastfat is disabled. On-disk candidate bytes
matched390 throughout the trial. This confirms configured/deployed identity,
not an independent live-memory image hash.

395 adoption and packaging remain HELD; no archives or accepted-state were
created.396 is a distinct original0101 control with setup settling before
file work, preserving this failed run and every original gate.
