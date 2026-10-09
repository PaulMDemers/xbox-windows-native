# Measurement boundaries after actual setup idle

Physical193 refused all measurements after five minutes of pending installation.
It is closed/restored; its candidate remains prohibited. Its immutable original
gates are unchanged. SetupAPI appended real no-driver searches during boot, so
merely extending that kit's deadline would not meet its equality gate.

This new helper preserves the actual setup API guard and five-second stable idle,
queries at every sample boundary, unchanged five v8 probes and original guarded
restart. It visibly instructs the person to close known hardware wizards without
disabling devices. The preflight deadline is explicitly fifteen minutes; timeout
or any unexpected API result refuses measurement/restart. No UI control or driver,
device policy, service, dump, mode or cache change is introduced.

After stable idle it copies the actual Windows setupapi.log to setup-before.log;
after five probes it copies setup-after.log. Both copies require actual idle before
and after, reject an existing destination, reject a source larger than16MiB and
record source length and FILETIME. Read/write chunks are bounded at4096bytes; high
file-size bits, short reads/writes, growth and changed final size refuse restart. The snapshots must be byte-identical in the
future cold audit, not merely ASCII or similar filenames. Their source size,
timestamps and complete log stream must agree. A failed copy refuses restart.
These checkpoints identify the measured interval; complete before/after boot
SetupAPI/event/hive history must still be preserved independently. Successful copying alone does not qualify the snapshots or establish an atomic
view against same-size concurrent edits: runtime guards and exact cold audits are
both required.

Any new scoped comparison protocol must explicitly document its interval gates
and preserve whole-boot strict failures (including Ft49 and Srv2013), rather than
pretend they pass. No physical protocol or candidate permission is implemented by
this preparation. Do not import synthetic emulator device policy to hardware or
rewrite193's failed gates. No release/storage/crash recovery qualification follows
from a pixel/timing comparison.

Before hardware: review compiler/provider/source pins, exercise actual production
gate boundaries at the new deadline, validate fresh idle and pending emulator
children and bookend equality with full cold integrity audits. Preserve old failed
cases and physical0101/video0093, original0088 and immutable0.1.0.
