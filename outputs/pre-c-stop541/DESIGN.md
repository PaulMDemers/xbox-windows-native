# 541: hold immediately before Xromwell's first C function

The checkpoint is at 02600200, replacing the existing five-byte jump to
BootResetAction (02600420). The original stack setup and all bytes from 026000f0
through 026001ff are restored/preserved from the pinned374 build. That interval
clears BSS and IDT RAM, loads IDTR, initializes the FPU, and writes existing MTRR
and control-register values. It is not changed to fix a suspected defect.

The existing490 marker at02680000 is reused after this interval. Its record and
matching guard now require mask5f: green, amber, green, amber across four phases.
Its success return is replaced by CLI/HLT/backward JMP/NOP; failure still halts.
The earlier wrapper's amber indication is unchanged. No first-C or Windows code
is intended to execute. Polls/transactions are bounded; the final hold deliberately
is not time-bounded. Watcher and manual reset availability are required.

This removes the earlier post-stack marker's I/O and delay before the interval.
It therefore is not a one-variable causal comparison with540. A positive new
indicator supports arrival at this checkpoint in this instrumented run, without
attesting both transaction status values or HLT. A missing indicator cannot
separate initialization failure from an LED transaction failure. There is no
retrospective ordinary-boot diagnosis or reliability qualification.

Only five exact byte spans, four same-length namespace strings, and the XBE
section digest change relative to the never-executed490 build artifact. Sizes,
payload copy length, allocation, loader, and all other bytes stay identical.
Inverse transformation reconstructs490 exactly. No closed runtime is reused.

The source and map identify memory/interrupt/PCI/AGP/cache/CPU/EEPROM setup before
video initialization inside BootResetAction. Black screen alone cannot locate a
failure among those later steps. If this checkpoint is observed, later C-entry
checkpoints can narrow them in subsequent fresh tests; no patch is implied.

Host tests execute actual clearing/arithmetic bytes with explicitly modeled
CR3/CLTS/LIDT/WRMSR/WBINVD effects. They check exact memory ranges, canaries, MSR
operands, register results, and a DF-set negative case. Marker tests execute
actual code with modeled SMBus/TSC over success/busy/error/deadline and IF/DF
combinations. Neither test proves physical cache, mapping, interrupts or devices.

Stage only under unique owned E:/Applications/XWNBoot541a. Preserve720p, ordinary
launcher/startup and Xbox C exclusion. One SITE command with20s reply bound;
never retry an accepted/uncertain launch. After observation request manual
poweroff/on and dashboard confirmation, then fresh paired files/receipts and
five-hive/event audit. No startup hook is installed or normal Windows restart
expected. All earlier runtimes remain closed; automation stays paused.
