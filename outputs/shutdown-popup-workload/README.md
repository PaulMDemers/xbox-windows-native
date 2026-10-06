# Hard-error observation on the failing rehearsal workload

This experiment reuses the exact immutable input from
[fatx0098-soak/rehearsal](../fatx0098-soak/README.md), whose cold event delta
contained the rundll32 DLL-initialization popup. It does not substitute the
clean 120-second helper used by the installer/token investigations. The original
result remains preserved. The fixture has FATX0098 and video0093; it is an emulator
fixture, not a capture of the current physical registry.

The unchanged helper performs 527 mapping checks, 16 synthetic BMP API cases,
50 final files, 34 absent intermediate files, and 15 timed rounds at four-second
intervals before requesting normal restart. Its minimum duration is 60 seconds,
not the physical soak's 15 minutes. Actual application/UI testing is separate.

Run 001 observes only native/kernel hard-error entries and kernel shutdown.
Run 002 adds native process creation, resume, termination and exit sites. Neither
changes guest results, registers, drivers, registry or device policy. Observation pauses the emulator and
can alter scheduling. Capture resolves the owning process through its own page
tables, supports relative process parameters, and retains unreadable data as
unknown. User hard-error capture includes the caller, bounded stack/frame values
and indicated Unicode parameters. Frame walking may be incomplete where frame
pointers are omitted; it is not a symbolic stack unwinder.

Run.ps1 owns a fresh numbered emulator disk and rejects a used attempt. The
supervisor launches Windows once and waits for dashboard return. After a runtime
capture identifies NT, trace.py attaches to that owned instance. After runner
cleanup, audit.py checks exact workload output, normal shutdown, event deltas,
payloads, matched system binaries and five structurally traversable hives.
It always leaves ordinary_run_valid false because this is a debugger experiment.
It never waives popup records. Full allocation auditing remains a separate step.

The physical FATX0098/video0093 baseline, normal startup, original0088 rollback,
immutable0.1.0 and physical soak3 strict failure remain unchanged. No physical
launch or FTP access is part of this experiment.

## Reproduced result

Run 001 reproduced the original popup. Three observations were captured: an
ExRaiseHardError call, its internal ExpRaiseHardError call, then kernel shutdown.
The two hard-error entries share status0xc000026b, thread0xff9dd580 and rundll32
PID1008/EPROCESS0xff9b4020. The command names newdev installation of
PCI\VEN_1B36&DEV_0005\...\03. One new EventLog popup has the exact original title
and window-station-shutdown message. These are two observations of one error,
not two popups. This fixture's device identity must not be assigned to the
physical Xbox's popup without physical evidence.

The caller0xa007e406 belongs to the captured win32k.sys module. Matched owned
instruction bytes show the preceding call to ExRaiseHardError with0xc000026b;
the following code requests current-process termination with0xc0000142. That
following request is static evidence, not a separately captured termination.
The PE image length0x192e00 and runtime module extent0x193000 agree after page
rounding. Cold before/after hashes verify win32k and all other reviewed modules.

The unchanged workload passes all527 mapping checks,16 BMP API cases,50 exact
files,34 absent intermediates and15 timed rounds totaling at least60000ms. Five
hives remain structurally traversable, payloads match, and one normal shutdown
precedes dashboard return. Nevertheless diagnostic_checks_passed is false due
to the popup. No full allocation scan or physical qualification was performed.

The prior token-lifetime runs show a clean failure for the01B4 installer. This
run proves the actual popup is raised from win32k in a different installer; it
does not capture when that process was created/resumed relative to shutdown.
Do not remove a device, disable its installation, alter
FAILEDINSTALL or suppress the popup just to obtain a passing event log. A proper
device package or shutdown synchronization change requires its own explicit
behavior, provenance and validation.

## Lifecycle control

Run 002 added four kernel lifecycle sites and captured 312 events. It did not
reproduce the popup. Event 66 observes services.exe entering the resume path for
the PCI10DE:02A0 installer, PID828/EPROCESS0xff9df020. Events217–218 observe CSRSS
requesting its termination with0x40010004 and that process entering exit handling.
Event223 then observes services.exe entering NtCreateProcess. Event227 identifies
the later PCI1B36:0005 installer, PID884/EPROCESS0xffb3f020, as the target of a
services.exe termination request with argument5; event228 observes its exit.
There is no captured resume-site hit for that later PID/EPROCESS and no hard-error
entry. Argument5 is not treated as the original creation error. Token lifetime
was not traced, so the earlier token-race finding cannot be assigned to this run.

The control passed the same workload, cold identities and five-hive checks,
with one normal shutdown and dashboard return. Its diagnostic checks pass;
ordinary_run_valid remains false. A clean debugger control does not override
run001's reproduced failure or the physical soak's failure. The change in
observation sites may influence timing; these runs do not prove why their
outcomes differ. Neither gives the failing installer's full lifecycle.

Next use the identified win32k caller and installer identity to narrow lifecycle
observation during the shutdown interval. Avoid another broad trace that adds
hundreds of unrelated thread resumes. Capture the failing path before choosing
shutdown synchronization or a properly sourced device package as an intervention.
Keep emulator-specific PCI identity separate from physical evidence; do not
deploy a patch or repeat a hardware soak on the strength of this clean control.

Both owned runners, supervisors and tracers finished. Source/caller review,
cold audits and cleanup are summarized by review-evidence.py and summary.json.

## Sparse follow-ups

Run003 uses seven sites: the three kernel hard-error/shutdown sites and four
umpnpmgr boundaries (create call, create return, process wait return, control
entry). review-sparse-sites.py checks those boundaries, imports and local-variable
offsets against the owned binary and existing disassembly. No generic process
creation/resume/termination sites are armed. It captures nine events:

- Events0–1: creation of PCI10DE:02A0 installer succeeds, returned PID0x340.
- Event2: its process wait completes with0 at tick7925.
- Event3: next creation targets PCI1B36:0005 with token0x8ac at tick7926.
- Event4: another services thread enters PnP control5 at tick7930.
- Event5: creation returns false/error6 at tick7931; saved token is now0 and
  PROCESS_INFORMATION is zero. Close/query internals were not traced here.
- Later control entries and kernel shutdown follow; no hard error or popup.

Run004 removes the call, wait and control observations. Only create returns and
the three kernel sites remain armed. It captures three events: successful GPU
installer creation, failed PCI1B36:0005 creation with error6/saved token0, and
kernel shutdown. Call entry and token-close timing are unknown in this run.
Even this return-only control does not reproduce run001's hard error. Do not
attribute the different outcome solely to breakpoint count or claim repeatability
of the popup from these controls.

Both complete the unchanged workload and pass cold diagnostic checks:527 mappings,
16 BMP API cases,50 exact final files,34 absent intermediates,15 rounds>=60000ms,
one normal shutdown, matching payloads/system binaries and five traversable hives.
Neither is an ordinary-run pass, a full allocation scan, a15-minute soak, or a
physical result. Their source snapshots, launch/cleanup records and separate
sparse-summary.json reports are under003/004. All owned sessions have finished.

The failed hard-error run remains authoritative evidence. There is no new driver
fix and no hardware deployment. Further similar clean traces have diminishing
value: next address the incomplete device installation through the real installer
in a disposable fixture, then retest the original workload and consecutive boots.
Use the FATX0098 correction already validated in fatx-paging-eof; the old package
checksum failure was resolved there. This is a new intervention requiring its own
control, not retroactive qualification of an existing package. Emulator-specific
devices and the earlier diagnostic audio flags remain explicit limitations.
