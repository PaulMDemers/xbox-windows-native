# Restart and original launcher review

The exact installed HAL distinguishes quick reset (SMC command 01), power cycle
(40), and power-off (80). Seven executions of its actual compiled dispatcher in
an isolated host instruction emulator agree with the reference source: firmware
actions 0/1 select 80, action 2 selects 40, and action 3 selects 01. Three invalid
actions reach the error path. Each execution stops before the helper or first
error-report call; no device access, firmware restart or Windows execution occurs.

The retained HAL hash matches the protected installed baseline checked in534.
GNU objdump inspection independently identifies the dispatcher and power helper;
Capstone decodes the complete dispatcher used by the execution test. The retained
300 HAL source supplies readable reference semantics, not a claim that build300
produced this installed HAL. Its power helper disables interrupts, submits the
SMBus command and halts. Both the initial busy wait and transaction-completion
wait lack a finite iteration bound. That is a shutdown robustness concern, but
does not itself explain the next launch failing after a confirmed dashboard return.

The exact proprietary Windows kernel was inspected locally by hash, without
publishing its bytes or disassembly. A limited static inventory finds direct
references to HalReturnToFirmware, including immediate action3 arguments. This
does not identify the UI path or prove which action our physical runs used.
Do not equate the Windows menu label Restart with HAL enum HalRestartRoutine.

The original ordinary XBE, hash6240a801..., performs five kernel calls before
entering its privileged loader: two contiguous allocations, two physical-address
queries and one virtual allocation. Its actual compiled prefix has no conditional
branches checking those returns. The first payload copy precedes CLD; later loader
copies explicitly clear DF. These are assumptions worth observing, not evidence
that an allocation failed or DF was set on the failed532 launch. No guard or CLD
patch was installed. The successful490 diagnostic previously recorded allocation
results and CPU state, but its predecessor power condition was not controlled.

After this prefix Xromwell's retained374 BootResetAction source initializes PCI,
AGP, cache/microcode, memory sizing, EEPROM and video before showing its normal
banner. A black screen alone therefore cannot distinguish entry, memory handoff,
early device initialization or later display failure. Source expectations are
not runtime evidence that those actions completed on532.

The532/533 success/failure/success and534 two power-cycled successes remain the
physical evidence. No claim of deterministic alternation, root cause, boot fix,
GPU support or additional successful hardware test follows from this review.

Next diagnostic: compare the already qualified490 preparation/CPU recorder under
explicit warm and cold predecessor conditions, using new owned namespaces and
identical instruction/data layout. Collect allocation results, copy comparisons,
the pre-witness and post-witness CPU contexts, refusal records and independent
Windows/shutdown evidence. Those contexts precede final handoff and do not prove
page-table contents, descriptor contents, the packet's own close, or device state.
Instrumentation adds memory and IO; even two successes would not qualify the
ordinary launcher or prove the recorded CPU fields caused the alternation.

This review made no console connection, file mutation, build or launch. Evidence
is audit001.json and its source. The tool availability search found no WSL rg;
grep was used instead. Two guessed historical script names did not exist and were
then resolved by listing the existing kit; no experiment depended on those reads.
