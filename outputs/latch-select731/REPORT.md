# 731: CR22 read-plane dependence control

Prepared2026-10-27 after730. This is a kernel-context measurement, not a native
mode switch, Windows launch or change to the full-mode validation predicate.
No CR22 or CR33 data write is present.

## Question and source basis

Does CR22's readout vary when the VGA graphics read-plane selector is changed?
The [pinned Envytools register database](https://github.com/envytools/envytools/blob/f102b82381f3f11cee113d16374c87091db039d9/rnndb/display/nv_vga.xml)
names GR04 READ_PLANE_SELECT and CR22 MEM_LATCH. The
[pinned Bochs VGA implementation](https://github.com/bochs-emu/Bochs/blob/67980ad8f2775e80e6913d4f94b2e85fa4fe701f/bochs/iodev/display/vgacore.cc#L1049)
implements the standard four-plane selector and reads the selected latch atCR22.
These support a bounded selector experiment, not an NV2A CR22 write contract.
Full source identities are retained through730's reference manifest and731's
source-review001.json. No unknown high bits are masked or assigned meanings.

Additional web queries did not yield a verified NV2A write specification. Scoped
workspace/reference-source filename searches did not identify a provenance-matched
5838 kernel for private inspection. This is not an exhaustive host inventory.
An exploratory C:/Homebrew/xemu path did not exist. No kernel/firmware binary was
retrieved, inspected, published or used as programming state.

## Exact operation

The existing checked kernel720p scaffold establishes PCI mappings, mode geometry,
and ownership of every framebuffer page. It writes exclusive E-only records.
In a bounded IRQ-off section the probe records actual CR0/3/4 and incoming flags,
then saves CRTC/graphics index selectors, GR04, CR22, CR33, CR1b and680630.
GR04 values outside0..3 cause refusal without a data write. Otherwise it requests
planes0/1/2/3 once each, verifies each full GR04 readback, and records first,
direct and reselected CR22 reads. It performs exactly one full saved-GR04 restore
after the admitted loop, including an early selection failure, then checks all
saved data and both selectors. Incoming flags are restored before kernel/file APIs.

At most five GR04 data writes are possible. There are no CRTC data, timing,
blanking, gate, unlock, interrupt-control or CPU-control-register writes, and no
legacy VGA memory-aperture access. The diagnostic does not preload latches.
Framebuffer drawing happens afterward through the established kernel allocation.

43 raw words are saved durably, with exact-file reread verification, before the
15-second status picture and automatic firmware return. Green means the selection,
capture and restoration checks completed, not that a specific latch hypothesis
passed. Orange means selection/cleanup mismatch, red refusal/selector failure,
magenta a result-file failure. See schema001.json for raw fields and statuses.

Different CR22 readouts would support selector dependence in this context.
Identical readouts remain inconclusive: latches could contain the same byte, or
CR22 might not depend on this selector here. Neither outcome proves CR22 write
effects, an appropriate expected byte, native-mode cause or Windows1.6 support.

## Validation and state

Fresh nxdk build with pinned SDK commit;27 actual COFF cases cover constant and
distinct plane data, all four initial planes, direct-read disagreement, refused
high bits/CPU contexts, failed selection/restore and changed saved state. Dynamic
access checks forbid all data writes exceptGR04 and enforce result/stack bounds.
The longest modeled critical path is879 instructions; this is not physical timing.
2353 compiled layout cases passed. Probe/layout/main nonrelocation instruction
bytes match the linked PE and XBE. Source/build/reporting review and pins passed.
No build/model/review failure. Any transfer/launch outcome is recorded separately.

The source scaffold is reused from729, never its closed binary or runtime.
Private build/config remain C:/xwn731. Remote destination is the unique owned
E:/Applications/XWNMode731. No startup hook, ordinary launcher change or access
to console C. See stage001.json and NEXT.md for current admission state.

## Physical result: CLOSED

One accepted launch at 2026-10-27T19:44:57.582684+00:00. The user observed
"Green and returned to dash" without a manual reset. Seven new records were
collected once with double-read checks; audit001 passed source/build/stage pins,
framebuffer ownership, report ordering and unchanged unrelated directory entries.

| GR04 requested and read back | CR22 first | Direct reread | Reselected read |
| --- | --- | --- | --- |
| 0 | FE | FE | FE |
| 1 | E7 | E7 | E7 |
| 2 | 5A | 5A | 5A |
| 3 | FF | FF | FF |

All values are hexadecimal. Four distinct stable values establish GR04-dependent
CR22 readout on this 1.6 in the measured kernel context. This is consistent with
the selected-latch interpretation from the pinned references. The measurement
does not establish CR22 write effects or generalize these bytes to other runs.
A fixed FF readback predicate is therefore not a context-independent test of
ordinary byte storage: plane selection changes the observed byte without a CR22
write. This does not identify the first failure of closed native runs708/709.

Status0731; four completed selections and five GR04 data writes including restore.
GR04 restored0, CR22 FE, CR33 11, 680630 3 and CR1b85 exactly match their saved
values. Both index selectors restored. Actual critical CR0=80010031, CR3=0000F000,
CR4=00000610; incoming/critical/restored EFLAGS=246/46/246. These are actual probe
readings, distinct from earlier preparation context. No CR22/CR33 data write,
blanking, timing, native handoff or Windows execution occurred.

The console is at UnleashX; no startup hook, owned host process or VM remains.
Automatic firmware dashboard return is recorded, not normal Windows shutdown.
No build/model/review/stage/launch/collection/audit failure occurred in731.
One documentation lookup used the nonexistent repository-root STATUS.md; the
actual outputs/engineering-notes/STATUS.md was then read. No evidence was lost.
Do not relaunch, recollect or parent this closed runtime. All prior failures and
closed runs remain preserved; no functional mode-switch validation was changed.
