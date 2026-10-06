# Installer lifecycle trace

This is an owned, debugger-interrupted xemu experiment. It cannot qualify an
ordinary boot, filesystem durability, the physical display driver, or a popup
fix. Physical FATX0098/video0093 and the immutable 0.1.0 recovery remain unchanged.

The child derives from video-direct-map-002, which preserves the earlier audio
installer queue. Preparation upgrades only its FATX0088 driver to the verified
FATX0098 EOF fix and stages the already reviewed shutdown-diagnostics helper.
All five system hives, video0096 and Microsoft framebuf are unchanged during
preparation. This is not the physical machine's registry or graphics baseline.

The helper observes five samples across 120 seconds and requests normal restart.
No automatic wizard dismissal, forced process termination, driver installation,
FAILEDINSTALL edits, cache cleanup or event-policy changes are performed.

`sites.py` pins observation instructions to the owned kernel and PDB layouts.
The resume site follows successful thread-object lookup, before KeResumeThread;
the thread's owning EPROCESS comes from the matching ETHREAD layout. It proves
the intended resume target, not successful thread execution. Creation calls may
fail. The existing termination site resolves the actual target after successful
handle lookup. Exit and hard-error observations retain the originating process.

Target command lines are read through their own page tables with QEMU physical
memory mode, restored after every read. No CR3/register/argument changes are
used. Missing/nonresident parameters remain explicitly unknown. All breakpoint
pauses change scheduling, so a clean trace cannot explain an intermittent race.

Each single launch and dashboard return belong in its numbered `launch.json`. Trace,
runtime, cold event comparison, helper log, SetupAPI and hive traversal evidence
belong under that case. Supervisor never repeats an uncertain launch. Its owned
emulator runner records cleanup and retains the private disk.

## Observations from the two lifecycle traces

Both independent launches reuse the same immutable input fixture. Run001 recorded
394 breakpoint events; run002 recorded433. Both reached NtShutdownSystem, resumed
the guest, returned to the dashboard and passed the bounded cold artifact checks.
Neither reproduced a popup. These are debugger observations, not ordinary PASS
qualification or a resolution of the prior physical failure.

Run002 resolves the queue transition directly:

1. Event337: CSRSS requests termination of PID916, the01B0 newdev installer,
   with status0x40010004 during shutdown.
2. Event339: that process enters its exit path. Event341 observes its later
   exit cleanup in the services.exe thread that managed the installer.
3. Event344 is a services.exe NtCreateProcess call; event345 resolves the new
   rundll32 PID720 targeted for termination by services.exe with exit status5.
   Its command line requests newdev installation of PCI10DE:01B4.
4. The new process still has relative, unnormalized parameters. No initial
   NtResumeThread observation for it was captured. Its appearance and termination
   establish a late creation attempt, not successful installer execution.

Run001 has the same late second-rundll32 pattern, but its original decoder could
not read unnormalized parameters. Those unknown values remain unknown in001;
the command from002 must not be retroactively assigned to001's process.
`001/trace-source.py` and `002/trace-source.py` preserve the executed decoders.

`parameter-review.json` pins the owned ntdll normalization routine: when bit0 of
ProcessParameters.Flags is clear, its nonzero command buffer is relative to the
parameters block. The revised host reader adds that base without writing guest
memory. Run002 directly records both pointer representations. Process identities
include EPROCESS plus PID because PIDs are reused during this very shutdown.

The owned ntdll message table identifies the exact earlier popup wording as
0xc000026b. That identifies the message, not its runtime caller. Neither lifecycle
trace reached a kernel hard-error observation site; the popup race remains open.

Run003 reduces instrumentation to the three hard-error sites and NtShutdownSystem,
using the same guest input. Its purpose is to reduce debugger scheduling changes,
not to claim that absence of a popup proves a fix. See003 for its actual outcome.

Run003 completed normal shutdown and dashboard return with one captured kernel
shutdown entry, no hard-error hits and no popup in the cold event delta. Its
helper, payload and five-hive checks passed. It additionally verifies both the
kernel and ntdll hashes in the exact guest fixture and final disk against the
reviewed binaries. All owned processes are closed; summary.json records cleanup.

These three clean observations do not resolve the prior strict physical failure.
Next inspect the late CreateProcess failure/unwind and window-station shutdown
path in the matching owned user-mode binaries, then capture the failing branch's
caller/status without hiding the queued device or suppressing its error. A
status5 exit argument alone is not a captured CreateProcess return value.
