# 668: allocator, boot interrupt state and UDP admission review

This is a source and exact-linked-function audit of667 artifacts. It creates
no new Xbox binary and never connects to the console or opens a closed guest
runtime. The source tree and all inspected files/binaries are pinned in
audit001.json. The prior physical667 observation and its limits remain intact.

## Finding

The diagnostic's caller and sender currently disagree about CPU interrupt
state.667's user-observed code indicates IF clear before memory detection and
set immediately afterward. The existing malloc/free normal paths execute
CLI followed by unconditional STI; they do not restore the incoming IF.
The native sender requires IF clear and returns A656_CPU before PCI/NIC work
when it observes IF set. This is a demonstrated diagnostic integration mismatch,
not a proven Windows boot or480p failure cause. More firewall changes cannot
make this particular rejected invocation transmit. Other network failures remain
unqualified because this invocation never reached the transport.

Do not replace the interrupt check with nInteruptable==0. That C variable gates
some handlers only. Timer and VSync do work regardless of it; SMC also ignores
it, accesses the shared I2C controller and can call display initialization twice
for an AV-change event. Actual delivery or collision during667 was not measured.
The result explains why the existing guard is materially useful; it does not
prove that a specific interrupt caused any previous failure or LED anomaly.

## Boot ordering and corrected interpretation

The exact linked reset order is IDT/PIC setup, PCI initialization, AGP setup,
cache disable/microcode/cache enable, memory detection, EEPROM read, video,
then the later explicit BootPciInterruptEnable. The diagnostic export is in
the video path and holds before that later explicit enable point.

BootInterruptsWriteIdt programs the master PIC mask to zero and the Xromwell
slave mask to0xaf, and calls intel_interrupts_on. Despite its name and nearby
comment, that helper reads/writes APIC-base MSR0x1b to disable the local APIC;
its linked body contains no STI, CLI or POPF. The initial commentary suggesting
that it enables CPU interrupts was incorrect and was corrected during review.
BootPciPeripheralInitialization contains CLI. CPU IF, PIC masks, local APIC
state and nInteruptable are separate controls and must not be conflated.

Memory detection contains the relevant malloc/free calls. The source inventory
also finds allocations in legacy encoder/video and later loader paths. A global
allocator change could affect many callers, not only this UDP experiment.
Prior664 linked tests separately preserve the free(NULL) IF-clear anomaly;
this review neither fixes it nor assumes it was taken in667.

## New evidence

audit001 passed10 static checks and17 fresh isolated linked executions:

- Twelve handler cases cover nInteruptable0/1 for timer, VSync, guarded IRQ4,
  and SMC no-reason, AV-change and power-event branches. Timer increments and
  VSync's write to modeled0xfd600100 occur at both values. IRQ4's print is
  suppressed only at zero. SMC still queries I2C at zero; the AV branch calls
  modeled display initialization twice and the power branch requests its
  expected I2C command sequence.
- Five sender-entry cases execute the actual NativeSend656 instructions with
  modeled CPUID/CPU initial state. IF-set cases return CPU rejection with
  NativeResult656.used==0, no PCI/helper/port accesses and IF preserved. An
  IF-clear compatible CPU reaches SGDT, where the harness deliberately stops.
  Missing features and an inadmissible CR0 reject before that point.

Handlers are invoked as C functions, not delivered through real interrupt gates.
I2C responses, timer progression, video calls and CPUID are modeled. VSync writes
only Unicorn memory. No test accesses real device ports or emits packets. These
tests establish linked control-flow behavior, not live interrupt delivery,
DMA coherence, elapsed hardware time, physical NIC readiness or Windows support.
The IF-clear control is not a pass of the segment/cache/PCI/DMA admission stages.

Exploratory reads initially used a nonexistent boot/BootInterrupts.c path and
Windows wildcard directory operands; corrected paths were resolved with rg.
No conclusions depend on failed reads. No executable/source mutation occurred.

## Next design, before another hardware test

Keep ordinary boot/allocator behavior and existing sender admission unchanged.
Work in a fresh host-only candidate on an explicit terminal transport phase:
freeze and validate the original capture first; separately record the original
CPU interrupt state; define any deliberate post-capture interrupt exclusion as
a transport effect rather than silently rewriting the diagnostic evidence.
Re-run all existing admission checks against the actual transport state. Do not
substitute expected firmware values, clear display pending bits, or waive gates.

Before such a phase is eligible for hardware, specify and independently test
entry failures, nesting/reentry, frozen-buffer immutability, exclusion duration,
cleanup and held-state behavior, including what happens when DMA cannot stop.
An interrupt-state transition needs an explicit review and linked proof; this
audit has not implemented one. Maskable-interrupt exclusion would not by itself
prove absence of NMI/SMI or solve other admission failures. A general allocator
fix and a working UDP diagnostic are separate changes and separate evidence.

No new physical test is justified merely to repeat667's clear-to-set finding.
Console remains last confirmed at UnleashX; no hook or owned host process.
Persistent firewall, ordinary720p, savedXBOX480, releases and recovery retained.
Ftdisk49/Popup26 remain unresolved. All prior failures and closed runtimes stay
preserved. This source/linked audit is complete; no native acceleration claim.
