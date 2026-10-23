# 669: host-only terminal transport prototype

668 established that the current observed caller state fails the sender's
IF-clear admission before PCI/NIC work. This prototype defines an explicit
post-capture transport phase. It does not change the allocator, existing sender,
admission policy, display capture, ordinary launcher or any installed file.
It is not linked into Xromwell and no XBE or console launch is produced.

## Contract

The caller supplies a complete, successfully validated772-byte encoded capture
after the original observation is finished. seal669 copies it into an original
record and a separate transport buffer. This completion argument is a caller
contract, not a substitute for the existing encoder/receiver checksum checks.
The native integration must establish that contract at its actual callsite.
Storage is owned, zero-initialized, valid/aligned and not shared for other uses;
input and callback pointers must be valid. This is not an arbitrary-pointer API.

Atomic phase transitions admit sealing once and transport once. Calls during
sealing, an active transport or the final held state return BUSY without changing
the owner or CPU state. Missing arguments/callbacks reject before claiming.
Once claimed, every core exit enters HELD; no retry or ordinary continuation is
allowed, even when NIC cleanup reports safe. The C core returns only to permit
host checks and a future bounded status indication before the terminal hold.
An actual noreturn native caller remains to be implemented and validated.

The proposed i386 entry helper records EFLAGS, executes CLI, then records the
transport flags immediately. That is an explicit diagnostic transport effect
after capture, not an original CPU observation or a workaround applied to boot.
The core requires a successful entry with flags differing only by removal of
IF, confirms live IF clear and checks the packet copy before invoking send.
It retains both samples separately and never rewrites the encoded original.

The send callback must invoke the unchanged NativeSend656 and copy its actual
admission/result/error values. It must not set admitted by fiat, invent cached
firmware values, clear display pending bits, or skip any later gate. The native
adapter is not present in669; tests model this callback. After it returns, the
core checks IF and packet bytes again and retains all fault bits. Unsafe DMA
cleanup takes priority in the displayed status but does not erase other faults.
Contradictory result fields are rejected. Three completed transmissions report
SENT, which is a local callback outcome and never evidence of LAN delivery.

## Terminal state and bounds

The native candidate has no STI or POPF and never restores IF to resume Windows.
irq_hold669 deliberately disables maskable interrupts and loops on HLT. Manual
recovery would be required. Unsafe cleanup forbids reuse of DMA storage; even
successful cleanup does not permit boot continuation in this diagnostic design.
No hardware is being placed in that state by these host tests.

The wrapper has fixed-size packet comparisons, a finite number of atomic steps,
one entry call, at most one send call, and at most two flag reads. Its callbacks
must terminate. Existing656 finite polling budgets still need integration
validation; they bound software operations, not a bus transaction that never
returns. The prototype has no honest hardware wall-clock upper bound. CLI
excludes maskable interrupts only; NMI, SMI, exceptions and physical device
behavior remain outside this model. No PIC/APIC or control-register changes
are introduced in the helper.

## Validation

The pinned GCC12 host build passed ASan/UBSan with40 lifecycle cases covering
both incoming IF states. These exercise entry failure, wrong sampled flags,
live IF still enabled, pre-send and post-send buffer mutation, nested entry and
sender calls, admission/no-use/send/incomplete outcomes, cleanup failures,
post-send IF change, combined faults, inconsistent result fields and refusal
of a second seal/run. Fifteen additional argument/phase checks verify rejected
calls never reach entry or sender. Original capture/input bytes remain exact.

The core also compiles freestanding i386 with the actual legacy include set,
without undefined runtime helpers. Object review confirms atomic CMPXCHG and
no privileged interrupt-control instructions in the portable C core.

Six fresh Unicorn cases execute the exact new linked assembly helpers with
different initial IF/arithmetic flags. They verify original and post-CLI flag
samples, ABI stack/nonvolatile-register preservation, the flag reader and IF
clear at the terminal HLT. No instruction is executed on the host's real CPU
with kernel privilege. These are isolated helper tests, not delivered IRQs,
boot tests, native admission qualification, DMA proof or physical networking.

Build/source/artifact pins and logs are retained in host001/linked001. All host
processes closed and the build lease released. Only small C-host/WSL artifacts
were allocated after checking the backing-volume reserve. The console was not
contacted; it remains last confirmed at the dashboard from closed667. Firewall,
ordinary720p, startup, savedXBOX480 and releases/recovery are unchanged.

## Next

Use a new host-only integration attempt. Bind the core to the actual native
sender and result structures, preserving every admission check. Validate exact
packet sealing/encoding at the caller, actual i386 wrapper/assembly/callback ABI,
single-call ownership, post-capture ordering, bounded status indication and
noreturn hold on every claimed path. Independently exercise all admission gates
and sender cleanup failures. Do not label a new interrupt-masked transport
sample as the original capture. No hardware staging is qualified by669 alone.
