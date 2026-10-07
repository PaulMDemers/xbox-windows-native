# Crash-dump usage notification fails below the FATX handoff

2026-10-07. Emulator-only diagnostic evidence; no physical access or driver edit.
All five fresh children use the pinned0101 FATX and0093 video binaries, with
HidServ restored from the owned0.1.0 archive. The settled emulator's synthetic
null-device/unsupported-device policy remains inherited and explicitly limited
to the emulator. Nothing here resolves the original111-byte non-ASCII physical
SetupAPI damage or establishes the unknown first restart method.

## Observed path

serial002 captures IopConfigureCrashDump in smss.exe: the initial handle
reference succeeds; IoGetDumpStack returns0xc00000bb; the shared caller error
branch logs0xc0040031, unique error3. IopCompleteDumpInitialization is never
entered. The initial static lead had considered only one incoming branch to
that shared error block. The full disassembly in static-path.json includes the
other branches and corrects that incomplete view.

serial003 narrows the path through IopGetDumpStack. The volume opens, SCSI
address/partition/layout queries complete, and IOCTL_SCSI_GET_DUMP_POINTERS
(0x41020) completes successfully with40 bytes. Initial STATUS_PENDING returns
are preserved separately from the effective completed statuses. Returning
STATUS_NOT_SUPPORTED from IoGetDumpStack alone did not establish which request
failed, so a new case was used rather than guessing.

serial004 captures the miniport dump-driver loader returning success, followed
by IopSynchronousCall for major0x1b, minor0x16, InPath1, usage type3: the
crash-dump device-usage notification. That call returns0xc00000bb; the same
negative status reaches the dump-stack return and Ftdisk49 branch. No pagefile
query or retrieval-pointer FSCTL is reached on this path. The absent VFAT
FSCTL_QUERY_RETRIEVAL_POINTERS handler remains a possible later limitation,
not the cause of this observed event.

serial005 additionally pins resident candidate0101 VfatPnp instructions.
The request parameters and file object match the captured usage request.
VfatPnp forwards IRP0xfe58b948 to device0xfe65b470, owned by
\\Driver\\Ftdisk at0xfe492000, and receives STATUS_PENDING(0x103).
IopSynchronousCall ultimately returns STATUS_NOT_SUPPORTED. The exact source
and binary show the filesystem clears its completion flag and passes this
request down; this trace does not identify the lower driver that originates
the eventual status. It would be incorrect to label Ftdisk itself as the
rejecting driver, to claim a failed write, or to fake successful PnP completion.
These addresses are specific to serial005, never future breakpoint inputs.

## Preservation and validation

serial001 is a retained diagnostic failure: its trace assumed the error caller
must have a paired IopCompleteDumpInitialization return, asserted, removed
all breakpoints and resumed the guest. No events were saved before that
assertion, so it supplies no usable return-value evidence. Later tracers save
the raw event before pairing assertions. No old guest was relaunched.

serial002/003/004/005 have4/20/23/26 captured sites, matching relocated resident
instruction bytes with kernel timestamp, thread/frame and return checks.
verify-traces.py replays instruction pins against the owned kernel and0101
binary and verifies the preserved failure plus observed status propagation.
All tracers ended, removed every breakpoint and resumed their guests.

Each of the five cases completes the same serial workload:792 appends,
32 queried allocation decreases,132 reopens and11 exact cold files. Each has
normal shutdown and dashboard return, full allocation consistency with323
directories/6765 files/324 directory clusters and zero errors/orphans, five
structural hives and protected payload hashes. Six installed storage binaries
(ftdisk,disk,atapi,scsiport,classpnp,diskdump) match before/after each run.
Source snapshots, private disk hashes, parent pins and closure records are
retained. Debugger timing means these are not ordinary performance results.

Every strict qualification remains FALSE because the sole new warning/error
is Ftdisk49. HidServ remains running at both workload checkpoints and SCM7000
is absent. No event, service, dump setting or hardware policy was suppressed.
The first Windows-host oracle command lacked the WSL-only dependency; it was
run correctly under WSL before launch. An early serial003 audit was rejected
by its cleanup guard before opening the live guest disk; it was performed
once after cleanup. These host failures did not become qualification passes.

## Next discriminator

Follow the SAME usage IRP through Ftdisk and the lower disk/port stack, capturing
entry/return and final completion before the IRP can be freed. Pending status
must not be substituted for final status. Resolve actual loaded module ranges,
pin resident instructions to cold verified binaries, preserve asynchronous
thread switches, and bound dynamic breakpoint ownership/teardown. A fresh
child is required. Do not patch a filesystem or storage handler merely to
satisfy the strict event gate. A real dump-support change would need successful
configuration and controlled end-to-end dump/readback validation, not only a
quiet log. Physical baseline and ordinary mapped-write evidence remain intact.
