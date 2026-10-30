# Loader826: fresh early Xromwell mode integration

Candidate only. No Windows desktop or physical result yet. Closed825 supplies
source-qualified mode transaction and user-visible native transition evidence;
it is not reopened or runtime-parented.

The candidate branches at the beginning of BootResetAction, ahead of legacy
PCI/AGP, EEPROM, display and filesystem initialization. The pinned assembly
startup still runs first. It establishes flat segments, paging off, cache-disable
bits, MTRRs and the loader stack. The full-image host fixture executes that
assembly into the admission code; modeled devices do not prove real timing or
cache behavior. The original XBE allocation/bootstrap remains unchanged and its
kernel allocation behavior is not covered by the assembly-startup fixture.

The transaction separates incoming scanout from destination physical03700000,
which is the linked nine-MiB framebuffer reservation. Both identity addressing
and actual CPU state are checked; this is not an nxdk allocation claim. Existing
heap, firmware, stack and initrd limits exclude the destination. Incoming scanout
must be page-aligned above02800000, within64MiB, at1280x720x32 with5120 stride.
Its address and layout are checked before an early-refusal report can draw.
The stricter transaction also checks the qualified GPU/context/CR baseline.

PCI IDs, command bits and BARs are read with CF8 restoration. Native byte reads
check cable and EEPROM configuration; an Xcalibur block read checks response.
No inherited SMBus flag is cleared. Polling is bounded and only the current
transaction's terminal flags are acknowledged after BUSY clears. The PM timer
check establishes progress at the known board clock contract, not new frequency
calibration. Invalid state refuses instead of entering legacy setup.

On success the target holds the green720x480 pattern. An admission or baseline
refusal with a validated incoming framebuffer draws an orange13-row report:
magic, phase, error, flags, CR0, CR3, CR4, incomingbase, status, completedreads,
transactionphase, transactionerror, blockentry. MSB first, white1. A later failure
reblanks and holds; black alone does not localize the failure. No LED encoding,
startup hook, reset command, Windows path or automatic return is installed.

Build001 failed because the new SetGPURegister collided with the legacy symbol.
Its source snapshot and private tree remain. Build002 namespaces the new symbol;
910 transaction and43 entry/assembly model cases passed. Build003 adds bounded
early-refusal reporting and excludes incoming framebuffer overlap with firmware
or stack. Its actual linked image passes912 transaction cases,32770 reservation
cases and47 entry/assembly fixtures. These are host evidence, not physical proof.
Closed host executions are not rerun; source-only test-port histories are kept.

Public source and records only. Binaries remain private under C:/xwn826.
Ordinary launchers and protected720p are unchanged. A successful826 still needs
a fresh continuation integration through FreeLoader and the Windows miniport.

Frozen imported gpu_preserving.c retains its historical trailing blank line;
gpu_types.h retains historical mixed indentation. Narrow attributes preserve
their exact compiled bytes while checking new source normally.

One SITE accepted at2026-10-30 05:25:10UTC with200 response. User observation
pending; deliberate hold, no Windows and no hook. No repeat launch admitted.

CLOSED FAIL: user observed black holding. Power off/on followed by authenticated
dashboard collection passed unchanged staged bytes and unrelated directories.
No native memory result or Windows evidence. Entry inherited layout remains
unproven:825 explicitly selected720p,826 did not. Fresh read-only probe next.
