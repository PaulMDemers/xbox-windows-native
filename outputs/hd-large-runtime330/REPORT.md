# Large-area emulator workload passed its scoped gates

The single new330 run completed all five samples with all15 extended327 cases:
fill, RAM upload, overlapping screen copies in both directions and real WM_PAINT
at256x128,640x360 and960x540. Independent full RGB/source/guard checks and
counter coverage passed. Legacy copy/text/window checks passed too.

The guest used1920x1080x32,pitch7680 and completed the six audio phases.
The combined audio/video interval contained no warning/error events. There was
one normal Windows shutdown and a dashboard return, followed by orderly xemu
exit0 without fallback termination. Cold allocation reported327 directories,
6763 files,328 directory clusters and zero errors/orphans. All five hives and
protected-file/policy/binding/history gates passed. The known whole-boot
Ftdisk49 remains the sole strict failure; scopedPASS is not strictPASS.

The recovered322 emulator and release binaries have their original exact hashes.
The new329 parent is explicitly a reconstructed never-executed fixture, not the
unavailable old317 container. Only replay.exe changed for330. The helper,
drivers, setup policy and runtime watchdogs stayed unchanged.238 source and11
host/media pins were checked before and after. Inherited fixture descriptions
are clarified separately in metadata-clarification.json; frozen inputs remain
unchanged and actual files/protected/helpers maps govern the audit.

All owned330 sessions are closed: preparation86822, runner83443/PID22052,
observer2513 and cold audit90946. The accepted launch and actual return times
are in emu001/launch.json; never relaunch, recollect or parent this runtime.
The immutable preparation can be used only to create a separately identified
fresh child when a new discriminator warrants it.

These elapsed times are emulator measurements, not Xbox performance. The new
probe is now qualified for a distinct physical measurement.331 prepares that
measurement with the original physical wizard helper and fresh rollback capture.
No rendering-driver optimization or GPU acceleration is claimed by330.
