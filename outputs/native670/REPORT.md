# 670: actual sender integrated in an isolated host fixture

Host-only integration passes 40 isolated i386 cases and 97 artifact/scope
checks. No XBE, console connection, installed change, boot or physical packet
delivery. This closes the modeled-send-callback gap in669; it does not qualify
deployment. All processes started for this kit exited; the build lease released.

## What executes

The frozen host003 ELF links the unchanged655 packet encoder,669 lifecycle and
IRQ helpers,656 native inspection/admission/NIC sender, and658 bounded SMC
writer with the new integration.c. prepare670 encodes trusted stable RAM into
a local packet, then seals separate original/transport copies. Failed encoding
and repeated preparation preserve the existing record. terminal670 calls the
actual NativeSend656 once and copies its actual admission and result fields.
It indicates the outcome with at most two bounded SMC writes and enters the
noreturn CLI/HLT loop. Rejected/repeated terminal entry holds without indication.
No branch returns to Windows, resets, retries sending, or restores IF.

Original packet data remains separate from deliberately changed transport
state. The saved original_flags sample is at transport entry, AFTER encoding;
it is not relabeled as the earlier capture's flags. The input packet's pre/post
capture fields are preserved byte-for-byte, including on failures. CLI excludes
maskable IRQs only; no NMI/SMI or physical exclusion guarantee is established.

## Test boundaries and observations

execute003 uses fresh Unicorn function fixtures, not xemu boots or previously
closed runtimes. Actual x86 instructions execute for the codec, lifecycle,
SGDT/segment reads, native wrapper, admission, polling core, port access and
terminal path. CPUID, MTRRs, RAM/GDT/register state, PCI helper responses,
NIC registers/descriptor release, timer and SMC responses are explicit models.
PCI helper symbols are UD2 test boundaries intercepted by the harness, not
deployable helper implementations. WBINVD executes in the model and is counted;
this proves no physical cache coherency, DMA visibility, PHY link or delivery.
The host linker layout is synthetic, not the final firmware layout.

| Coverage | Result |
| --- | --- |
| Entry with IF set and clear | Original/transport samples differ only by IF; three locally completed frames; exact original packet, independently checked IP/UDP checksums |
| CPU, segment, cache, PCI admission rejection | No native NIC MMIO or PCI command writes; actual admission codes retained |
| DMA admission | Deliberately corrupted modeled admission input is rejected before NIC use; no naturally bad physical DMA layout claimed |
| Invalid/null config, used sender, invalid codec | Rejection retained, no extra transmission; null config does not enter NativeSend656 |
| Frozen/backward timer, missing PHY/link, stuck setup/MII/TX, TX/IRQ errors, occupied descriptor | Exact expected native errors retained; finite fixture execution and final hold |
| Stop failure and final PCI-command readback mismatch | Unsafe result retained; hold, no continuation |
| SMC busy/error/timeout | Failed indication retained separately; sender result remains intact; hold |
| Transport corruption before claim | Guard rejects before sender |
| Transport corruption injected at native entry | Original remains intact; corrupted transport is detected after sending; no claim that memory corruption cannot reach the wire |
| IF re-enabled at native entry | Native CPU rejection plus wrapper IF fault, no SMC indication, final hold with IF clear |
| Unprepared/claimed/held entry and actual second call after every hold | Record preserved; second terminal entry makes no additional sender, PCI, NIC, timer or SMC calls |

The synthetic capture has nontrivial data in every field. Its complete772-byte
encoding is independently constructed with Python struct/zlib and compared
against the original and emitted payload. Ethernet frames are814 bytes, with
three identical frames in positive cases. SENT means local completion only.
The capture producer itself is not run or quiesced by this fixture.

## Preserved failures and provenance

- host001: native.c compile stopped because the isolated include path omitted
  fs/cdrom/iso_fs.h. No executable or physical access.
- host002: native.c compile stopped on lib/eeprom/BootEEPROM.h. No executable or
  physical access. host003 uses the legacy Makefile's include directory list.
- execute001: harness incorrectly required one native call for null config;
  16 earlier cases passed. The null-config adapter correctly rejected before
  the native call. Original test/receipt retained.
- execute002: corrected harness,39 cases pass. execute003 adds preclaim packet
  corruption, actual repeat-terminal calls, exact native error assertions and
  explicit flags/packet hashes;40 cases pass. Production candidate unchanged.

host003.json pins all compilation inputs, compiler/tools, legacy headers,
commands and artifacts. Source files copied privately before compiling.
Original656 native/admission/core and669 lifecycle/helper bytes match their
retained sources;667 tracked source remains unchanged. review001 cross-checks
the linked binary, test source, receipts and boundaries. Build001/002 private
logs stay at C:/xwn670/host001 and host002; binaries stay private in host003.
No proprietary binaries, screenshots, hives, media or credentials in this kit.

## Remaining qualification

Next is a fresh host-only full-firmware callsite integration and review: prove
the exact capture producer is frozen before prepare670, pass the retained
attempt/build identity and configured EEPROM/network inputs, use the actual
PCI helpers and real linker BSS/DMA placement, and keep this terminal-only path
separate from ordinary startup. Preserve existing CPU/cache/admission gates.
Validate that image and its failure/hold paths before proposing a watched,
single-use physical attempt. This kit alone is not hardware-launch admission.

Console last confirmed at dashboard after667; no startup hook. Normal720p,
saved XBOX480, immutable releases and private recovery remain protected.
Permanent firewall remains installed; automation paused. Ftdisk49/Popup26,
Windows boot intermittency,480p root cause and physical UDP remain unresolved.
