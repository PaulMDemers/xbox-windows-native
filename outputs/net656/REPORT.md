#656 bounded sender and dormant native binding

The UDP sender is implemented and compiled into a fresh retained651 Xromwell
source export. It is deliberately **not called by the boot path yet**. The
private artifact is named DO-NOT-LAUNCH.xbe; it must not be staged as a working
network diagnostic. No console, guest image or existing runtime was opened.

## Implemented behavior

nic.c builds a single814-byte Ethernet frame: broadcast destination, configured
source MAC/IP/port, IPv4 TTL1 with DF set, checksummed IPv4/UDP headers and the
exact772-byte655 payload. Ethernet FCS is left to the NIC, as in retained
forcedeth. It sends at most three identical copies. Each TX descriptor must be
free before publication; the prior packet must finish before another is sent.
Descriptor errors and the NIC's TX-error status both abort the burst. A valid
descriptor release alone is not delivery proof; the independent receiver is
still required. No ACK, DHCP, ARP, kernel download or retry of a console launch.

The dedicated nForce sequence derives from retained Etherboot forcedeth.c
(Timothy Legge2004; Linux forcedeth Manfred Spraul2003), preserving its GPL2+
provenance. The old driver is unchanged. Setup stops both old engines before
publishing owned rings, masks NIC interrupts, disables bus mastering during
ring preparation, uses owned two-TX/four-RX descriptors and buffers, checks PHY
identity/link/autonegotiation and refuses an unsupported negotiated ability.
It retains normal receive initialization rather than assuming that TX can run
without it. RX traffic is bounded by four owned1536-byte buffers, not consumed
by application code or recycled during the burst.

Every wait has a finite iteration budget. delay656 reads the existing32-bit
3.579545MHz timer directly, rounds the requested microseconds upward, supports
32-bit wrap, rejects a large backward/discontinuous jump and fails after200,000
samples if the timer does not advance enough. It never calls legacy wait_us.
This bounds software callback counts, not a physical bus transaction that never
returns, and is not an independently calibrated hardware wall-clock guarantee.

Cleanup attempts both RX/TX stops even after a fault, checks busy clears and IRQ
mask, and clears PCI bus mastering using a WORD command write/readback. It never
writes PCI status bits through a dword command access. It preserves first failure
and cleanup failure separately; unsafe cleanup forbids continuation/reusing the
DMA memory. A later caller must implement the reset/hold decision explicitly.
The core's safe_to_continue is a policy result under observed I/O, not an
unconditional physical guarantee. An accepted/uncertain launch remains one-shot.

## Native memory contract and effects

native.c samples CR0, EFLAGS, stack, selectors/GDT, CPUID, MTRRs, PCI identity,
BAR/command and the actual linked BSS/DMA range before allowing NIC MMIO writes.
admission.c accepts only the retained flat32-bit, paging-off, IF-clear layout,
64/128MiB RAM, expected WB RAM/WC shadow/default-UC MTRRs, nForce10de:01c3 at
fef00000, memory decoding enabled and32-byte-aligned DMA storage wholly inside
BSS below the reserved stack. Unknown state is rejected; there are no CR0/CR3,
MTRR or interrupt-enable writes. The EEPROM MAC is already available before
BootVgaInitialization, so a future caller can use it without borrowing dashboard
network state. No private address or MAC is compiled into this source.

WBINVD is an explicit native transport effect after capture, before publishing
buffers/ownership and before reading DMA completion. Descriptor flags are volatile.
No uncached-alias assumption or page/cache reprogramming is used. The actual linked
buffer lives in its own static BSS allocation; the heap and stack are excluded.
The initial caller must freeze the source capture before any transport work.

Other explicit post-capture effects include NIC reset/configuration, receive DMA,
MAC programming, PHY reads, NIC/MII/TX/RX status acknowledgments, masking NIC IRQs,
and disabling bus mastering on exit. These are not passive observations or a
display-driver fix. No display pending bit is cleared to make a test pass. The
binding does not yet enforce its post-capture callsite itself: the unimplemented
caller is responsible, and no hooked/launchable image is claimed.

## Evidence and retained failures

- host001:2003 sanitizer checks,172 injected I/O positions. Closed before later
  volatile-descriptor and freestanding-header refinements.
- host002:2003 checks after volatile descriptor publication/readback refinement.
- native001:1037 admission checks passed; native compile failed because the old
  freestanding include set has no stddef.h. Exact source/tree/logs retained.
- host003:2003 checks after removing the header dependency, using GCC's offsetof
  and pointer-width builtins and asserting32-bit protocol integers.
- native002 compiled, but readiness review rejected implicit declarations of
  PciReadWord/PciWriteWord. The legacy header omits those existing helpers; the
  new binding now supplies their exact declarations. No permissive compile is
  promoted as qualification.
- native003:1037 admission checks and native compile with -Werror on the new
  modules passed. Existing make/RWX/Perl tool warnings remain in retained logs.
- host004:2007 sanitizer checks,175 independently injected I/O positions after
  adding the NIC IRQ TX-error check. Covers frozen/backward/wrapping timers,
  no PHY/link, stuck setup/MII/TX/stop, occupied descriptor, descriptor/IRQ errors,
  failed PCI command, frame bounds/checksums, one-shot refusal and cleanup faults.
- native004:source compiled with -Werror on new modules,1037 admission
  checks passed; old xwn_hd_native, xwn_hd_adapter, xwn_hd_profile and forcedeth
  .text/.rodata object sections remain byte-identical to651 (eight comparisons).
  This is object-code preservation, not identical final load addresses/timing.
- native005:final build adds explicit -fno-pic/-fno-pie only for the new modules,
  removing unnecessary GOT/thunk dependencies found in native004's object review.
  The same1037 admission checks and eight old-object comparisons pass. Static
  review verifies the only external native dependencies are the existing PCI
  helpers, BSS/RAM symbols and new core/admission functions; no implicit runtime
  helper, legacy delay, CR write, WRMSR, STI/CLI or POPF is present. WBINVD remains
  the declared transport cache effect. No object references NativeSend656 yet.

Native hardware instructions are compiled, not executed by these host tests.
No physical MTRR sample, DMA coherence/delivery, link negotiation, timer calibration
or LAN/firewall acceptance is established. The175 injected positions belong to
the modeled normal path, not every possible hardware execution path. Every
private build/test has a fresh directory; failures and closed fixtures are retained.

Research attempts: the guessed upstream nvnet.c URL returned404 and the GitHub
directory fetch was unavailable. No conclusion depends on those fetches; the
retained forcedeth source is the implementation reference. Several local searches
used nonexistent include/BootEEPROM.h or wildcard path operands (errors2/123),
then resolved exact paths with rg --files/reads. No files were changed by searches.

All processes closed and build lease released. No launch, FTP write, startup
hook, recovery change or active receiver. Original physical lease retained;
automation paused. Dashboard remains the last user observation from closed654.
Ordinary720p/startup, savedXBOX480 and all releases remain unchanged.
