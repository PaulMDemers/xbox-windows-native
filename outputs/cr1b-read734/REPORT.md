# 734: CR1b observations before cleanup

Prepared after physical733's full-byte rejection: expected05, observed85,
with680630 still2 and successful cleanup. No734 physical result yet.

## Source/access review

Linux v6.12 identifies CR1b as FIFO control and assigns the calculated burst
value to it. Its older NVIDIA driver maps arbitration0 to CR1b and calculates
that value from graphics burst size on NV10/NV20-class paths. This establishes
the field's broad purpose, not an NV2A bit7 read/write contract.

- [FIFO register name](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/nvreg.h#L233)
- [Burst programming](https://github.com/torvalds/linux/blob/v6.12/drivers/gpu/drm/nouveau/dispnv04/crtc.c#L905)
- [Calculation and state access](https://github.com/torvalds/linux/blob/v6.12/drivers/video/fbdev/nvidia/nv_hw.c#L647)
- [Pinned Envytools register database](https://github.com/envytools/envytools/blob/f102b82381f3f11cee113d16374c87091db039d9/rnndb/display/nv_vga.xml)

The Envytools offset1b occurrence in its G80 panel array is not the NV2A CR1b
definition. The inspected sources do not justify treating bit7 as reserved,
read-only, self-changing, or safely ignorable. Search results for unrelated
VGA chips were excluded. Private exact inputs and public hashes are recorded in
references001.json. No whole third-party source is added to this kit.

## Bounded question

Is05 observable immediately after the single CR1b05 write and across subsequent
reads while630 remains2, before any recovery write? New734 adds two bounded
blocks after733's last prefix data write:16 direct data reads with CR1b still
selected, a630 read,16 explicitly reselected reads, another630 read. No other
MMIO read occurs before or inside the first block. RAM stores and loop control
do occur. Then733's original ordered full-byte checks and recovery run.

The groups have a fixed order. Their differences cannot isolate selector effects
from elapsed time, prior reads, or changed instrumentation. No sample is a
timestamp. This does not repeat729's sampling after630 restoration, nor does it
waive733's rejection. Unexpected sample bytes remain raw evidence. Forward
status, cleanup mismatch mask, actual control registers and incoming/restored
flags stay separate. No extra CR1b data write, CR22/CR33 data write, native
handoff, geometry, encoder programming or full-mode replay is introduced.

## Preparation and checks

- Fresh nxdk build001; compiler/SDK pin and source hashes in build001.json.
-59 actual COFF execution cases, including four hypothetical read policies,
 all15 deferred mismatch positions,20 cleanup mismatch bits and admission /
 selector / flag checks. Hypothetical policies are not physical semantics.
-2353 framebuffer layout cases and actual main/probe/layout instruction bytes
 checked in both linked PE and XBE, excluding relocation operands.
-Independent112-word schema audit across59 cases;12 corrupted records rejected.
-Exact source reduction back to733 proves only observation initialization and
 the two read blocks were added to the probe. Main changes are report size,
 unique attempt/phase names and its inherited comment correction.
-All model instances finished; no owned VM/process. No preparation execution
 failures. Two generation issues were corrected before the first build/model:
 inherited main header and model counting of the initial write's selector.

Private build C:/xwn734/build001. XBE114688bytes:
583733dfe1e1feb169f023cb849dd270028b4e61eb3f96f9b3a59eb2d28ebbf0.
Source bytes frozen by sources001.json. Ordinary720p and Windows launchers stay
unchanged; no hook. This is not Windows1.6 or acceleration qualification.

## Physical lifecycle

Stage001 completed with exact remote readback; watcher readiness is pending. No
launch requested. Unique target
/E/Applications/XWNMode734; reports/E/xwn-mode734-*.json. Console C off limits.
One accepted/uncertain SITE request is never retried. Expected status display
15seconds then automatic dashboard return. Green means forward and cleanup
checks match; orange means a forward or cleanup rejection, with exact details
in the new report. Red is refusal/other failure; magenta is recording failure.
If held/black, preserve observation before reset. Collect once after return,
then run audit_collection.py; audit failure is retained, not overwritten.

All733/prior runtimes remain closed. No functional predicate change justified.
