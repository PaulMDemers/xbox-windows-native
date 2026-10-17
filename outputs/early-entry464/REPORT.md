# Early Xromwell marker: exact source and stack boundary review

The unchanged374 ELF sections reproduce the complete288316-byte deployed payload.
Seven original source files and the ELF symbols/disassembly were pinned privately
at E:/xwn464/source001. The existing414 source hashes match; no shared source,
SDK, installed launcher or console state changed during this review.

The actual payload begins at0x02600000 with a jump to start_linux at0x02600090.
The wrapper disables paging and jumps through its copied loader without rebasing
ESP. The original startup avoids stack operations until `mov esp,0x02800000`
at0x026000f0.462's actual saved pre-PUSHFD ESP was0xd001cd7c, well beyond physical
RAM after paging is removed. This is a constraint on new instrumentation, not a
newly demonstrated defect: the original sequence deliberately avoids stack use.
An ordinary C call or PUSH-based save at entry would therefore be unsuitable.

The original WriteToSMBus has unbounded waits for bus idle and completion despite
its outer50-retry counter. I2cSetFrontpanelLed discards both write results and
returns success. The old wrapper newflash debug path ends in an infinite loop.
None is suitable unchanged as a bounded, acknowledged, continuing diagnostic.
The normal red LED is first set after PCI/AGP/video initialization, so that LED
alone cannot distinguish the earlier entry boundaries.

No marker has been built or installed. No new Windows boot was requested, no
hardware ports were touched, and no boot cause was established. The fresh463 E
allocation scan separately passes.462 remains a successful diagnostic boot with
no refusal record;460's failure remains unresolved.

Evidence: [source and binary review](source-review001.json),
[design requirements](DESIGN.md), [next implementation](NEXT.md).
