# 488: unchanged privileged loader exercised in a diskless CPU fixture

The successful483 and failed487 physical runs have identical decoded preparation
records, including all saved registers, EFLAGS, allocation addresses and alias
backing790528. Their wrapper and witness sources are identical after only the
483-to487 namespace substitution. Raw primary differences are the three identity
bytes; witness differences are identity, poll count, TSC values and TSC-read count.
The same1024 loader bytes occur in both actual XBE files. No old evidence changed.

New lab003 executes those extracted instructions through paging disable, CR3
clear, descriptor-table/segment changes, far jump, full1MiB payload relocation
and entry into an independently authored oracle. It passes the synthetic
nonidentity dual-copy arrangement and an identity-mapped control. The oracle
checks the untouched invalid old stack before installing its own stack, CR0.PG,
CR3, all six segment selectors, GDTR, IDTR, LDTR, IF/DF and every relocated byte.
Seven deliberate faults and one short-copy oracle rejection are observed at the
expected boundaries. Independent review rejects96 lifecycle/identity/transport
mutations, rehashes88 reviewed inputs and leaves original captures untouched.

This is QEMU TCG with its Pentium III CPU model, a synthetic address space,
synthetic1MiB payload, masked PIC interrupts and no Xbox devices/kernel. It does
not reproduce physical caches, firmware interrupts or the unknown actual page
tables/control registers. Earlier466/471 already observed privileged entry in
xemu;488 adds a small isolated fault matrix and complete relocation oracle,
not a first-ever emulator handoff or a physical boot fix.

Intel's compatibility guidance recommends identity-mapped code across paging
changes. The recorded low address02000000 maps to physical000c1000; the wrapper
has another copy at physical02000000. Equal copies and a TCG pass do not prove
physical behavior. Conversely, the same arrangement succeeded in483, so its mere
presence is not a failure discriminator. Root cause remains unknown.

All20 diskless VM invocations across lab002/003 are closed; no disk, EEPROM,
Windows fixture or physical Xbox was accessed. Private artifacts are under
C:/xwn488/lab001..003. No SDK/shared source/installed launcher/startup/display
change, new XBE, Windows result or graphics qualification is added.

Preserved harness issues:

- lab001 failed assembly before any VM: `flat` was a GNU assembler pseudo-register.
  lab002 only renames the fixture label. The actual extracted loader is unchanged.
- lab002 met its original exit/marker predicates, but positive and short-copy
  cases executed the oracle's trailing UD2 before asynchronous QEMU exit took
  effect. These post-receipt faults are retained. lab003 replaces only those
  synthetic oracle tails with CLI/HLT loops and also requires no exception in
  those three cases. lab003, not lab002, supports the clean terminal result.
- review001 omitted end-TSC high bytes and the TSC-read-count field from its raw
  witness comparison allowance. It failed without changing evidence. review002
  corrects the offsets using the existing96-byte marker schema; its result is
  final-review.json.

Evidence: [independent review](final-review.json), [lab003 runs](run003.json),
[build and pins](build003.json), [failed comparison](review-failure001.json).
Architecture source: Intel SDM Volume3B, order253669-087, section24.30.3,
[page24-32](https://cdrdv2-public.intel.com/850979/253669-087-sdm-vol-3b.pdf#page=452).

PC486 remains a selected-input arithmetic characterization;484 exact endpoints
remain failed and487 supplies no Xbox alpha result. Console configuration is
unchanged; its last verified state remains487's dashboard return and hook removal.
