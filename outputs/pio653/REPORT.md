# 653: diskless ATA PIO prototype; not admitted to hardware

The receipt652 protocol now has a tested single-sector PIO backend prototype.
This is host work only. It does not provide automatic physical boot logging,
fix 480p, qualify a disk driver, or change the installed Xbox build.
No XBE, VM, disk image, FTP access or console launch was made for653.

## What changed

`pio.c` exposes symbolic register callbacks, with no physical port addresses or
IN/OUT implementation. Admission requires a fresh context, three distinct bounded
LBA28 sector addresses, IF clear, inactive bus-master DMA, no initial bus-master
error/interrupt indication, and an exact512-byte IDENTIFY match. It checks ATA,
LBA and FLUSH CACHE support, capacity, and rejects a reported long logical sector.
The identity and sector map in these tests are synthetic.

The backend enforces receipt652's `RRRWWFRRWFRRR` sequence. Each data command
transfers exactly256 words. It polls readiness with a finite iteration limit,
checks DMA/IF during transfers, honors failed reads/writes/delays, and refuses
further I/O after any error or uncertain completion. No reset, control-register
write, bus-master status clear or automatic retry is implemented.

The address validator checks arithmetic, partition/data bounds and distinct
slots. It does **not** parse FATX, establish file ownership, distinguish a live
Xbox E partition from C, prove non-overlap with other files, or establish that
the supplied map remains current. Passing it never authorizes physical writes.

## Validation

| Evidence | Result | Scope |
| --- | --- | --- |
| `host001.json`, `test.c` |25,999 checks passed under ASan/UBSan|Backend integrated with receipt652 against a RAM-only controller|
| `compiled001.json`, `compiled.py` |51 cases passed|Exact linked i386 backend against a separate Python controller model|
| Freestanding i386 object |No undefined symbols|Compilation/linkage, not a native caller or hardware binding|

The host suite injects failure at every one of the12,645 successful low-level
callback positions, before/after effects where the interface supports them.
The flags callback models failure by reporting IF set; it has no error return.
Additional cases cover each command's busy/error/data-ready/completion failures,
DMA state, last permitted poll versus timeout,512 different identity mismatches,
unsupported drive features, geometric limits and out-of-order writes.

The independent i386 execution verifies calling convention and IF preservation,
the complete13-operation sequence, exact modeled sector bytes,14 ATA commands,
3,072 data words,768 written words and26 explicit Status acknowledgments on the
successful path. It exercises policy refusal, aliasing, IF/pending IRQ admission,
identity mismatch, wrong order, busy/no-data/error/floating/zero/changed Status,
active DMA and callback failures. Every tested failure refuses a subsequent
read without another callback. Synthetic disk/cache updates are model behavior;
they do not establish real media durability or a successful Windows shutdown.

Sources and private artifacts are pinned in the result JSON. Private build files
are in `C:/xwn653/host001`. All processes exited and the build lease was released.
The projected20.02GiB host reserve was checked on output and WSL backing volumes.
No653 build/test failures occurred; earlier failed evidence is unchanged.

## Protocol review and admission limits

ATA normal Status reads acknowledge device interrupts; Alternate Status polling
does not substitute for every protocol Status read. The prototype makes those
acknowledgments explicit and requires `permit_status_ack == 1`. A zero/unapproved
policy is rejected before any callback. Model permission is not native permission.
Do not bind this to the early boot path under the existing no-pending-bit-clearing
constraint or describe it as a passive/read-only observation.

Primary reference: [T13 ATA/ATAPI-6 working draft1410D revision3a](https://www.read.seas.harvard.edu/~kohler/class/04f-aos/ref/hardware/ATA-d1410r3a.pdf),
sections7.3,7.8,9.5 and9.6 for Status/control semantics and PIO sequencing;
IDENTIFY word83 for command support. This is a working draft, not a claim of
certification against a final ATA standard. The logical-sector exclusion follows
the ATA IDENTIFY word106 description also given in the ATA pass-through material
of the [UEFI2.3.1 specification](https://uefi.org/sites/default/files/resources/UEFI_2_3_1_C.pdf).

The delay callback is only modeled. It still needs a demonstrated minimum400ns
and a finite maximum independent of the disputed display timer. An iteration
limit does not bound a hung callback, port transaction or CPU. FLUSH completion
latency and power-loss persistence remain unqualified. No native bus-master port
mapping, PCI decoding, disk selection, bus ownership or calling-context proof
exists here. A clear sampled DMA bit is not ownership of the controller.

Receipt652 still needs an independently verified live allocation, exact fresh
seed readback, private disk identity, quiescent RAM/stack ownership and an actual
bridge/caller binding. Do not bypass these requirements or initialize IDE ahead
of the display measurement merely to make the logger work.

## Console and project status

651 remains CLOSED: user-observed desktop followed by audited normal restart;
LED order was inconclusive. Ftdisk49 and shutdown Popup26 limitations remain.
The last console observation is dashboard after651; no fresh status probe was
made. Ordinary720p/startup, saved XBOX480, releases and recovery remain unchanged.
No hook, rollback, owned process or queued launch exists. The existing physical
lease is retained; automation is paused. No user action is needed for this kit.

Next is the caller/transport decision in `NEXT.md`, not another launch of651.
