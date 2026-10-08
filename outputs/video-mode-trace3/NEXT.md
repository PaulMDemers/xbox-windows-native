# Next bounded work

Same-mode DrvAssertMode disable/re-enable is now observed and qualified. It keeps
the same PDEV/primary surface. Do not describe it as surface deletion/recreation.
Windows enumerates only1024x576x32at60Hz in this fixture; do not invent another
supported mode or alter miniport mode policy solely to make a test pass.

The next useful ownership boundary is RAM0109 to boot-video/crash display. Design
a NEW sacrificial emulator child using the existing qualified controlled-dump
protocol, unchanged large-LBA storage stack and explicit one-shot trigger. First
inspect prior dump-write/recovery records and current bootvid/miniport pins; do
not relaunch any old crash case. Observe real handoff callbacks and raw framebuffer
contents, then require intended bugcheck/high-LBA dump writes and independent cold
allocation/hive/protected-file checks. Preserve the crash image; any recovery boot
must use a separate child. This is a plan, not an executed or qualified crash test.

Surface/PDEV replacement remains a separate gap. Investigate actual NT5 engine
lifetime behavior before selecting a legal API trigger; no direct DDI calls to
manufacture coverage. Four drawing hooks remain unobserved through real GDI:
FillPath,StrokeAndFillPath,Paint,StretchBlt. No new hardware/video-mode claim.

Debugger lessons: a single-step stop is not proof of retirement. Require bounded
observed progress with the removed breakpoint still absent and retain every reply.
Live virtual memsave can return a partial file; journal response and byte count,
never silently pad or substitute. This successful variant uses exact cold persisted
references plus runtime digests for its independent104-frame RGB oracle.

All four new cases CLOSED, all owned sessions closed. Physical0101/video0093,
original0088 rollback and immutable0.1.0 untouched. Remain emulator-only.
C: approximately21.8GB free (about20.3GiB): inspect capacity before any new build
or large capture and preserve the20GiB guard. Recover space only from verified
closed owned artifacts; never casually relocate qcow backing chains.
