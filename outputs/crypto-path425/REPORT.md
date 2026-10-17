# 425: actual security-state paths return STATUS_NAME_TOO_LONG

One fresh emulator diagnostic is CLOSED. Seven verified native checkpoints and
145 paired file API calls identify the failing directory and file requests.
Every observed call returned; none returned STATUS_PENDING. All debugger
breakpoints were removed, physical read mode remained0 and the guest resumed.
Windows then restarted normally to the dashboard; host exit0 was orderly.

| Stage / event | Actual request | Result |
|---|---|---|
| Direct names /30,31 | Create43- and69-byte components | `C0000106` |
| User RSA /83 | Create the44-byte user SID directory beneath `Microsoft\Crypto\RSA` | `C0000106` |
| Machine RSA /112 | Open-or-create the69-byte container file beneath the All Users `Microsoft\Crypto\RSA\MachineKeys` directory | `C0000106` |
| User DPAPI interval /130 | `services.exe` creates the same44-byte SID directory beneath the user's `Microsoft\Protect` | `C0000106` |

`C0000106` is STATUS_NAME_TOO_LONG. All five requests carry absolute native paths
and root handle0; no root-handle inference is needed. The directory requests have
FILE_DIRECTORY_FILE set and FILE_CREATE disposition. Machine RSA uses
FILE_OPEN_IF; earlier FILE_OPEN attempts under All Users and the system directory
return NAME_NOT_FOUND. Its leaf exactly matches the key file actually created
by the423 NTFS control. The high-level machine RSA failure therefore hides an
observed long-name failure inside the same owned probe call interval.

The user DPAPI service request is bracketed by the probe's DPAPI checkpoints and
uses the exact same user SID. This establishes the service's actual request and
status, but does not independently trace RPC call IDs, impersonation tokens or
the complete service-to-caller error translation. Do not relabel it a fully
paired RPC trace. No lsass file calls were observed by these four breakpoints.

Machine DPAPI's service requests use short S-1-5-18 and36-character master-key
components. The trace observes successful creation/opening of the master key and
Preferred. The cold probe log confirms exact immediate plaintext recovery.
Persistence across reboot remains the separate ordinary424 result;425 does not
repeat that second boot.

## Evidence and qualification

The original423 operation bodies are unchanged;425 adds module/PID/TID discovery
and no-inline stage checkpoints. Build002 is warning-free, native SHA256
`daebde3e2391f9dcf1e626d7081d7d539d2614488479a7c62ef6796c9ca32eda`.
All38 imports resolve against owned SP4 DLLs. Actual checkpoint/native headers,
ntdll header and four resident syscall stubs agree with reviewed inputs;13 pin
records cover seven checkpoints, two headers and four stubs. The independent
review checks each return address against the exact binary's checkpoint call.
Kernel process/thread fields match the native PID/TID at all seven stops.

The145 calls comprise120 from trace.exe and25 from services.exe. Pairing uses
thread, process, stack and API; no unpaired/incomplete calls remain. Relative
loader-search requests stay relative in the record. These are four selected
file APIs, not every syscall or all system I/O. Filenames, scalar arguments and
statuses are captured; private key/data buffers are not read.

Source closure matches the installed403 FATX binary318fc432... to its recorded
tree dc942ab4... and current public create.c/dirwr.c. The matching source returns
STATUS_NAME_TOO_LONG at its42-character/encoded-byte add-entry guards. This is
static source correlation plus an actual native syscall status, not a breakpoint
inside that driver branch. No driver or syscall behavior was patched.

Cold audit:6,557 staged files to6,564 final files;279 directories,257 directory
clusters, zero allocation errors/orphans, clean QCOW, five clean hives with
independent raw values agreeing,3,149 protected Windows binaries and probe exact.
Seven added files and18 runtime-changed existing files are retained in private
inventories. One EventLog6006, orderly dashboard return at01:25:49UTC, no host
timeout/fallback kill. Ftdisk49, kbdhid1 and the custom DRM typed-reader limitation
remain. **Strict qualification is false; ordinary qualification is false because
this is a debugger experiment.**

The cold native log reproduces all three424 creation errors: userRSA206,
machineRSA80090020, userDPAPI206; memory-only CSP and machineDPAPI succeed.
64 modeled parser/pairing controls and853 mutations of actual trace evidence
pass. All231 frozen inputs remain exact. No physical Xbox access, settings
change, provider replacement, filename renaming, event suppression or key/blob
transfer occurred. The physical720p demo remains unchanged.

## Retained harness failures and interventions

Build001 refused before compilation because a Windows environment value did not
propagate to WSL; build002 passed an explicit environment under the actual held
build lease. Sites001 refused a Windows-only Capstone DLL in WSL before reading
the disk; extraction and Windows static review were separated. Sites002 then
refused decimal versus hexadecimal disassembler formatting for ret8; sites003
parses the numeric operand without weakening the expected stack-pop size.

The tracer's first Enter was sent while the VM was stopped. No checkpoint fired.
A read-only running framebuffer capture showed the Run dialog still open with
the exact command. One further ordinary Enter while running launched the probe;
all seven stops followed. This is an explicit input-harness correction, not an
unreported launch retry. No SITE EXEC or guest executable was relaunched. An
initial HMP screendump observation failed because this build lacks that command;
its failed reply and missing-image conversion failure are retained. The later
physical framebuffer read did not pause the guest and is only UI evidence,
not a coherent pixel-content test. Hardware dialogs were unchanged.

See trace-verification001.json, source-closure001.json and emu001/audit.json.
Private runtime/build/screens are under E:/xwn425. Never relaunch or recollect
emu001. This narrows the problem to real long-name requests; it does not make
FATX capable of storing those names or qualify a lossless public clean install.
