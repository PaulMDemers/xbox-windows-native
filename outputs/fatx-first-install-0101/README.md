# Controlled first GPU installation on FATX0101

This diagnostic uses an actual retained pre-install fixture, not a settled hive
with its GPU binding deleted. The inventory in ../fatx-append-sequence verifies
that pre-install SYSTEM has ConfigFlags1024 and an existing XboxVnt5 service,
but no GPU Driver class binding. This is a retained bringup state, not a pristine
Windows installation. Historical emulator device policies remain unlike hardware.

Preparation uses the original shutdown-install-idle002 parent also used by the
prior targeted setup-completion experiment. It replaces FATX0098 with reviewed
0101 and replaces the idle observer with the exact previously tested004 helper.
SYSTEM, SOFTWARE, video trace, startup, video0093, framebuf DLL and GPU INF stay
unchanged during staging. The original fixtures and failed trials are preserved.

The unchanged helper samples installer windows for120 seconds. It may send one
Finish only to the fully matched successful GPU page, one No to that same
process's exact restart question, and one Cancel to the exactly identified
emulator1B36:0005 placeholder welcome page. It leaves other dialogs untouched.
Restart requires all three actions and the pending-install API to report idle.
Cancellation acknowledges an unsupported emulator device; earlier subsequent
boots proved it does not persistently resolve that placeholder.

This is explicitly a UI-assisted diagnostic, not an ordinary unattended stability
run. No physical-console access, host recorder, debugger or signing-policy edit.
Cold collection checks setup log growth/prefix and non-ASCII bytes, exact GPU
binding/INF, unchanged selected binaries, normal shutdown, event deltas, hive
parsing and full F allocation. Every launch is unique and retained. Neither a
clean result nor helper actions explain the original physical malformed bytes.

Tools: prepare.py001 (requires both append-sequence passes), Run.ps1,
supervise.py001, then trial.py collect001 and qualify.py after owned cleanup.
Probe source and import/build review are copied byte-exact from prior004; the
existing private binary is hash-verified, not rebuilt. Its compiler/build inputs
remain referenced in that review and the prior004 archive. Only source and
reports are tracked; raw media and logs stay private.
