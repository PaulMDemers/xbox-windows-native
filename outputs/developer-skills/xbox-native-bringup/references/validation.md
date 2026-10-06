# Validation and console cycles

## Keep evidence classes separate

Label physical-console results, reproducible emulator runs, debugger-mutated
experiments, isolated function tests and user observations separately. A GDB
register/memory change can locate a boundary but does not validate an ordinary
boot. A user reporting working ping establishes that observation, not bulk TCP
performance. Keep earlier failed attempts when a later candidate passes.

## Own the emulator instance

Use a private writable disk/overlay, EEPROM copy, config, logs, ports and output
directory. Record the immutable seed's hash and overlay backing chain. Moving a
qcow2 child can break a relative backing path; inspect the chain before starting
it. Retain required parents while failure evidence references them.

Use project resource leases for heavy builds and emulator lifetimes. Shared
functional slots are not performance isolation. Acquire the UI lease for direct
input/capture where the host provides one; target the owned PID and monitor port.
Do not attach to the only visible emulator without confirming its ownership.
Record cleanup and retain compact evidence rather than redundant full disks.

## Physical launch and collection

1. Resolve dashboard paths independently from Windows drive letters. Capture the
   exact installed payloads and rollback copies before deploying a new candidate.
2. Stage, read back and hash the intended changes. Scope writes to owned project
   paths. A dashboard menu edit needs a saved original and exact XML readback.
3. Give each test a unique marker/output path, preferably exclusive creation.
   Record whether launch was requested/accepted; a timeout is not permission to
   repeat the launch. Poll for return without launching another workload.
4. On dashboard return, disable one-shot test startup first, then preserve logs,
   before/after binaries and output hashes. FTP availability alone is not PASS.
5. Prefer a guest-requested normal restart after completion. A forced reset
   changes the durability question and must be recorded as such.

Some UnleashX FTP servers ignore the path argument to LIST: CWD to the target
directory, verify PWD, then LIST. Do not rely on displayed timestamps for freshness.
Capture exact replies and content hashes. Keep credentials in local config or
environment, not reusable skills or reports.

Include diagnostic-file lifecycle in boot preflight. Some bringup loggers accept
only a fresh seed and deliberately stop on records from a previous boot. Preserve
the old trace before reseeding; a used-file guard is not itself storage corruption.
For a repeat-boot fix, exercise consecutive boots without host resets of that file.
Inspect conditional compilation before disabling diagnostics: a trace flag may
also select functional PnP forwarding, PCI reads or callback wrappers. Remove
those effects separately; an emulator PASS cannot settle hardware-only dependencies.

## Persistence gates

Require workload completion, normal shutdown evidence and independent cold
readback. Check exact payload bytes, complete allocation ownership, and relevant
formats (BMP lengths, registry hives, executable hashes). A valid FAT chain may
still contain incomplete data; successful readdir is insufficient.

Compare event logs against the pre-run record boundary so historical delayed
writes are not attributed to a new run. Preserve event IDs, sequence/time and
decode limitations. If FTP remains offline, report the observable state rather
than infer a crash; ask once for the screen when that is the remaining evidence.

## Shutdown and incomplete device setup

A working boot service does not prove that its device has a complete PnP driver
installation. For shutdown-time rundll32 failures, correlate command lines,
SetupAPI logs and device-instance service/driver metadata before blaming the
recent kernel change. A pending installer can advance to another device when
one failed installation is acknowledged. An unchanged control may still pass
when the failure is intermittent; retain it rather than selecting only failures.
Configuration changes in disposable fixtures are diagnostic interventions,
not driver fixes or evidence that an unsupported device works.

When resolving a terminated process from another process's context, read its
user parameters through its own address space. Nonresident parameters remain
unknown. Breakpoint pauses alter shutdown timing and cannot qualify an ordinary
boot. Also verify the installed binary's provenance before applying findings
from a same-named open-source implementation to its private behavior.

A successful SetupAPI log can coexist with a completed wizard waiting for Finish
or a restart question. Inspect the owning process and visible control state.
When using CMP_WaitNoPendingInstallEvents on owned NT5 builds, verify the export
and check again near restart: an early idle result can precede later queued
installation. A guard that refuses restart is a held test, not a completed soak.
Complete supported setup first; distinguish an explicitly acknowledged unsupported
device from an installed driver. Do not silently dismiss unidentified dialogs.

For narrow diagnostic UI actions, verify the device/process identity, complete
page text, parent/control IDs and enabled state. Text line endings may differ;
normalize only the demonstrated formatting difference. Preserve a no-action
matcher miss rather than attributing a coincident clean run to the intended fix.
Follow setup with a subsequent boot without automatic dialog actions.

If shutdown stalls, preserve a post-deadline memory snapshot privately when lock
ownership is needed. Stack code candidates alone do not establish a lock cycle.
Correlate wait-block objects with resource owners; mark nonresident data and
undecoded ownership unknown. A logged EventLog shutdown is not dashboard return.

Deep relative qcow2 chains can work in Linux tools yet fail to open in Windows
xemu. Preserve the failed host attempt separately from guest boots. If shortening
a chain by copying a delta and rebasing only its backing path, verify virtual-disk
equality and unchanged originals before using a fresh attempt ID.
