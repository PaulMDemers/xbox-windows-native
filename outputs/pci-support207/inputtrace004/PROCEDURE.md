# Bounded input-port observation

Use a fresh exact copy of rebalance002's immutable veto source. Keep the
driver, HAL, INF, installer, helper and startup selector unchanged. Preflight
pins these dependencies, historical NT5 PDB layouts and actual kernel/class
images. The kernel arm address comes from inputtrace003's preserved live IDT
observation. Every interpreted site must match the loaded module header and
relocated instruction bytes of its pinned provider.

Observe class-driver calls to IoGetDeviceObjectPointer, the ZwOpenFile return,
and the final status. During those calls only, observe IRP_MJ_CREATE dispatch
and IoCheckShareAccess entry/failure/return. Record file/device/driver identity,
share counters and any earlier successful class-open output slot still present.
Treat failed reads as unknown. A device name or dispatch pointer by itself
does not establish a retained owner.

The observer uses memory reads, breakpoints, single stepping and continuation;
it has no guest data/register write command. Breakpoint pauses alter timing.
This is a debugger experiment, not an ordinary-run timing or boot qualification.
Stop observation after both class sharing failures, 240 seconds or 4096 loop
iterations. Remove breakpoints and resume; the runner has a 300-second host
bound. Host termination is not normal Windows shutdown.

Hold the cooperative exclusive xemu lease for the owned emulator lifetime and
the build lease for preparation/cold audits. Preserve all failed attempts and
immutable sources. Cold-audit allocation, protected files, five hives and log
history, then review actual captured calls without inferring uncaptured paths.
The resource-only runtime gates do not themselves qualify the trace.

Do not access the physical console, change device policy, integrate other
owners' code or relaunch a used runtime fixture.
