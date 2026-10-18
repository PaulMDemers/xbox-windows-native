# 542: preserve the C frame and hold before PCI initialization

541's observed green/amber indicator supported arrival before first C entry.
This fresh candidate intercepts the original five-byte CALL at026004f8, just
after MemoryManagementInitialization and BootInterruptsWriteIdt return, before
BootPciPeripheralInitialization. The earlier C code and its calls remain exact.
Original stack setup is restored, so no added post-stack marker runs earlier.

The reused diagnostic stub begins with five NOPs in place of MOVESP. It saves
flags/registers on the current stack, runs the existing bounded marker, restores
the state on success, then deliberately holds with CLI/HLT/JMP/NOP. The C frame
must remain intact: the checkpoint ESP is027fdf84, not02800000. No displaced PCI
call is executed because this is a terminal checkpoint, not a boot-through patch.

Record and matching guard require maskf5: red, amber, red, amber. Earlier wrapper
amber is unchanged. A matching observation supports this instrumented run reaching
the boundary; it does not independently attest HLT, both marker status values,
hardware correctness, prior failure cause, or ordinary boot reliability.

Six exact spans, four same-length namespace strings and section digest change
relative to the never-executed490 build artifact. Inverse transformation recovers
that artifact exactly. Sizes, copy lengths, padding and other loader bytes remain
unchanged. No old runtime is relaunched, recollected or used as a parent.

The original IDT function writes256 descriptors, programs both PICs and disables
the local APIC using its existing MSR sequence. Those operations are preserved,
not borrowed or changed as a proposed fix. Host tests explicitly model PIC/APIC
effects, not asynchronous interrupts or actual physical devices.

Twelve integrated host cases execute the real C prologue, memcpy, memory-manager,
IDT and marker bytes in a flat memory model. They cover two existing config
branches, enabled/disabled APIC inputs, missing-heap and DF-set negatives. Heap
contents and all256 gates match an independent source/map specification. Writes
outside allowed ranges fail. Candidate success preserves every saved GPR, ESP,
flags except terminal IF clearing, and all C frame bytes above ESP.

Forty separate marker cases cover two images, IF/DF combinations and modeled
success/busy/status-error/deadline paths. Candidate writes below the current
stack boundary are enforced, including frame canaries. Controller/capture tests
use modeled FTP. No host result is physical cache/mapping/interrupt proof.

One watched launch under unique owned E:/Applications/XWNBoot542a after exact
readback and baseline checks. Bounded marker followed by deliberate indefinite
hold; user must be ready to observe and reset. One SITE request,20s reply bound;
never retry accepted/uncertain dispatch. No startup hook or XboxC access.
Preserve ordinary720p/startup. After observation and confirmed manual reset to
dashboard, perform fresh paired capture, hive/event audit and close this runtime.
No Windows, D3D, GPU, game or release qualification is intended.
