# Late installer creation failure

Owned debugger experiment using the exact immutable fixture from
../shutdown-installer-trace. No physical access, driver replacement, registry
change or popup suppression. Video0096/FATX0098 in the emulator differs from the
physical0093 graphics baseline. Each run uses a new private disk and one launch.

Observation sites are pinned to matching kernel32, advapi32 and ntdll binaries.
CreateProcess calls and their return addresses are paired by ETHREAD; concurrent
calls at the same return address are not conflated. User-mode code bytes are
verified on a hit. Cold audits compare the full binaries against reviewed hashes.
All debugger pauses affect scheduling; these runs cannot qualify ordinary boots.

Run001 had two incomplete attachments, both preserved. The second localized the
host E14 read error to the instruction bytes at a breakpoint, not the command
string. The final attachment records unreadable sites, removes that breakpoint,
single-steps and rearms it, allowing the guest to handle the instruction fetch.
It does not force pages into memory or change CR3, return values or guest data.
All three attachments belong to the same Windows launch.

The final001 attachment captures PCI10DE:01B4:

- CreateProcessAsUserW receives token handle0x8f4 and flags0x8.
- The inner CreateProcessInternalW adds the suspended flag, gets a successful
  server response, and returns TRUE. Its returned process/thread handles are
  0x904/0x8f4, with PID736/TID900.
- advapi32 then terminates the new child, and the outer CreateProcessAsUserW
  returns FALSE with last-error6. The token argument equals the newly allocated
  thread handle; handle type/lifetime need further tracing.
- The termination argument5 is a constant in advapi32's cleanup code. It must
  not be labeled the original CreateProcess error or interpreted as proof of
  access denial. The exact creation call comes from umpnpmgr.dll, not a FATX
  driver routine.

Run001 cold checks show completed helper, normal shutdown/dashboard return,
unchanged reviewed payloads and five traversable hives, with no new popup. The
prior popup failure remains unresolved. The interior server-reply observation's
original `caller` field is actually the stack top, not a return address; do not
use it for attribution. Subsequent tracer code reads the enclosing frame's
return address correctly.

Run002 adds token-query/duplication returns. Its initial broad attachment reached
the bounded512-event limit during startup; a second attachment on the same boot
arms those sites only while services.exe is in process creation. Each source
version and attachment outcome is preserved separately. The second attachment
captured only NtShutdownSystem, without another late installer creation. Its cold
audit also passed the bounded diagnostic checks with no new popup. This control
does not answer the token-query question; no missing interval is inferred from
another run. Recurring baseline SCM7000/Ftdisk49 events are retained and explicitly
classified by the diagnostic audit; these checks are not the strict soak gates.

Matched umpnpmgr code loads the token from its saved global at RVA15b64. A
separate cleanup block closes that handle and later clears the global, under
synchronization that still needs investigation. Neither static ordering nor
numeric handle reuse establishes the responsible close or a race. Next, observe
the saved token's lifetime and native token-query results around a failing late
attempt, with minimal observer effects. Do not suppress the installer, alter
device policy or infer a popup fix from these clean shutdowns.

Both owned runners and their supervisors/tracers have finished. Cleanup and
attachment provenance are summarized in summary.json. Physical FATX0098/video0093,
normal startup, original0088 rollback and immutable0.1.0 remain unchanged. The
third physical soak's strict failure remains authoritative; no recovery capture
or hardware deployment followed these debugger observations.
