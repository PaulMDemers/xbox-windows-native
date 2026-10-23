# 671: terminal UDP integration in a fresh full firmware build

Host qualification:40 transport cases,12 export-entry cases and60 artifact/
linkage checks pass. Full Xromwell built from the pinned667 tree with unchanged
display, native sender/admission, PCI, allocator, interrupt and startup object
sections (34 matched sections). Compiled XBE remains private. Host results do
not establish physical transmission, cache/DMA coherency or a480p fix.

## Explicit post-capture boundary

At XwnExport657, the original hardware capture has returned. An atomic owner
claim rejects repeated/nested entry. The new boundary records FreezeBefore671,
executes CLI, and records FreezeAfter671. Only after validating that boundary
and live IF does the bridge copy the saved producer RAM into Frozen671.
It then copies the EEPROM MAC and retained configured source IP/port, encodes
the unique attempt/build identity, seals the packet and enters terminal670.

This is an explicit diagnostic change AFTER hardware capture and BEFORE its
RAM copy. Existing capture flags remain original. The later transport-entry
flags now normally show IF clear; they are distinct from FreezeBefore671 and
the earlier capture fields. This cannot retroactively make earlier capture
operations atomic. NMI/SMI and device DMA are not excluded by CLI. Reentrant
capture before this boundary remains a limitation, not silently resolved.

The need for this boundary follows668's actual interrupt-handler audit: SMC
handling can re-enter video initialization despite nInteruptable==0. No PIC,
APIC, allocator, general driver, display-pending-bit, or ordinary boot change.
The diagnostic never resumes Windows or restores IF. All owned failures hold.

## Exact linked tests

execute001 runs40 fresh isolated Unicorn function fixtures against the actual
full image. Real PciReadDword/PciReadWord/PciWriteWord instructions execute;
the harness models their CF8/CFC port responses. No host UD2 PCI stubs exist.
The linked BSS/DMA addresses are used unchanged. CPU/MTRR/GDT, NIC descriptors,
timer and SMC are modeled. Gates, packet checksums, three local completions,
cleanup errors, lost IF exclusion, corrupted packet and repeat terminal paths
are checked as in670. WBINVD in a model proves no physical cache visibility.

entry001 executes actual XwnExport657 with synthetic saved producer RAM for
success/unsupported/failure results, IF set/clear, CPU/cache/PCI rejection,
cleanup failure, invalid codec identity, re-entry and two injected freeze
failures. The bridge runs only with verified IF clear; encoding follows the
copy; original input bytes and earlier IF-set capture fields remain unchanged.
Every second export entry holds with no additional I/O. The hardware capture
producer itself is not rerun by these isolated fixtures. Unchanged display
object bytes and linked ordering establish its callsite placement.

Build and tests passed on their first671 attempts. Earlier670 compile/harness
failures remain preserved. build001 pins source tree, compiler, configuration
identity header, commands and artifacts. The build_id is an externally assigned
manifest token, not a binary self-hash. Actual network configuration is retained
privately and checked against the receiver manifest; no credentials published.

## Watched physical attempt

The user confirmed availability to watch and reset. physical.py owns only
E:/Applications/XWNLatch671 and private C:/xwn671/physical001 before/after
evidence. No Windows startup hook. Full stage readback and protected baseline
checks precede one SITE request with a20-second reply bound. Accepted/uncertain
requests cannot be repeated; controller-review001 tests both cases.

The receiver listens for180 seconds with an exclusive socket and exact671
identity/peer/candidate pins. Permanent firewall verification is read-only.
No ACK or receiver-triggered launch. A format-valid packet needs independent
launch/stage/observation reconciliation before hardware attribution.

Indication: solid green means the local sender reported three completions;
red/off means admission rejection; red/amber means unsafe sender/cleanup state;
solid amber covers other failures. SMC indication can itself fail. Screen is
deliberately held; user power-cycle is required. LED alone is neither packet
delivery nor raw CPU/readback evidence. See actual launch/run/capture records
for current state; this report does not presume a successful physical result.

Normal720p/startup, savedXBOX480, immutable releases and private256 recovery
remain protected. Ftdisk49/Popup26 and boot intermittency remain unresolved.
