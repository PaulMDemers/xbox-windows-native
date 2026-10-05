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

## Persistence gates

Require workload completion, normal shutdown evidence and independent cold
readback. Check exact payload bytes, complete allocation ownership, and relevant
formats (BMP lengths, registry hives, executable hashes). A valid FAT chain may
still contain incomplete data; successful readdir is insufficient.

Compare event logs against the pre-run record boundary so historical delayed
writes are not attributed to a new run. Preserve event IDs, sequence/time and
decode limitations. If FTP remains offline, report the observable state rather
than infer a crash; ask once for the screen when that is the remaining evidence.
