Build-Core001 initially failed PowerShell parsing at an unquoted comma in
`-fsanitize=address,undefined`, before script execution, lease acquisition or
artifact directory creation. Build-Core001-refused.ps1 preserves the failed
source. The corrected script quotes that argument. No guest/physical action.

Initial primary-source fetches for hw/xbox/mcpx_smbus.c and mcpx_aci.c returned
404; actual upstream paths are hw/xbox/xbox_pci.c, amd_smbus.c and mcpx/aci.c.
No conclusions rely on the missing files.

The corrected Core001 request found the shared build lease busy after creating
its empty artifact directory. It performed no compile. Core002 moves directory
creation inside the lease. Several Core002/Core003/Driver001 requests also found
the lease busy before directory creation and backed off; they did not bypass it.

Core002 eventually compiled and passed67617 ASan/UBSan host cases. model001
started a new paused xemu, verified SMBus identity/class/BAR and absence of modem,
then Windows rejected the RosBE-built host transport PE with WinError193. No
SMBus transaction, guest boot or installation occurred. The emulator was closed,
private EEPROM was unchanged, and all logs/config/disk/PE/source are retained.
model-test001-host-failure.py is the exact failed harness. Core003 changes the host
transport to a Linux executable run through WSL pipes; the C engine is unchanged.

Core003 never acquired its lease and was not built. model-pe.py instead executes
the already-compiled Core002 x86 through Unicorn with only CRT/I/O hooks. model002
failed before any SMBus transaction because pefile sorts sections by RVA while
COFF indices use original header order. model-pe002-failure.py retains the defect.
The corrected parser uses header offsets; model003/model004 are new successful
paused device-model attempts, not rewrites of001/002 or Windows loader evidence.

Driver001 failed-Werror=multichar on the pool tag before producing a driver.
xwnsmb-driver001-compile-failure.c is preserved. Driver002 replaces the same tag
with numeric0x37626d53; kernel compilation/fixup succeeded, but the probe failed
because WIN32_LEAN_AND_MEAN requires explicit winioctl.h for IOCTL definitions.
xwnsmb-probe002-compile-failure.c and xwnsmb-driver002.c preserve those sources.
The001/002 resource-check design is independently rejected before any installation:
checking after lower START does not protect the HAL from BAR relocation.
Candidate003 constrains the known BAR1 requirements before allocation and checks
the start resources before forwarding. No earlier candidate was installed.

Driver003 passed 2,954 constraint adversaries and compiled/fixed the constrained
kernel, then probe linking failed on unresolved memset with -nostdlib. Its exact
probe source is retained. Driver004 reuses the pinned003 kernel and compiles the
corrected volatile-byte-clear probe and explicit SetupAPI installer. Full package
static import/forwarder/dynamic lookup review passed; no runtime claim follows.

Native001 preparation initially found the shared build lease busy before running
Python or creating fixture outputs. A bounded waiter backs off without bypassing
the cooperative lease. No guest action follows a lease refusal.

During native001, two optional read-only framebuffer capture attempts failed.
The actual xemu monitor has no screendump command. First attempt asserted before
saving the reply; second preserved the raw response under private artifacts and
its hash in native001/capture-failures.json. No input, debugger or guest change
was performed, and no screen observation is claimed. Native001 runtime evidence
comes from the actual guest logs and independent cold audit.

An inline host Python command intended to derive the repeat-boot probe failed
PowerShell quoting before writing any file. The source was subsequently created
by a normal file copy and explicit patch, then compiled as cycle001.

Native002 completed fresh live telemetry from retained binding, but its genuine
pending-install gate returned258 for the bounded interval. It made no normal
restart request. New SetupAPI names unresolved audio01B0; the global pending API
does not prove that this is the only queued device. Host closure and all raw logs
are preserved. This is an integration-blocked shutdown qualification, not a PCI
functionality failure and not a completed ordinary/persistence cycle. Ftdisk49
also remains the inherited strict whole-boot failure on both native attempts.

Delivery: repeated large Git pushes stalled after authentication; both the
devkitPro MSYS2 Git and native Git for Windows paths were tried. Owned stalled
processes were closed. A sanitized HTTP trace (only method/length/status/error
lines, no authentication headers or bodies) is retained privately. Remote main
had advanced to an object absent locally. A normal no-tags fetch updated only
remote tracking/object state, leaving the assigned branch/worktree unchanged.
The next native Git push sent105 objects/124.17KiB and succeeded, versus the
earlier10663-object/8.61MiB attempts. This establishes the successful delivery
path, not a proven root cause of the prior transfer stalls. No force push,
global safe.directory edit, main change or tag modification was used.
