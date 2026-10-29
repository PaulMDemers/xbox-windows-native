# Kernel CR18 line-compare low byte:812

Purpose: extend the qualified810 source prefix with the pinned704 helper's
CR18 low byte (m=0x3ff), verifying eight neighbors and reversing the new write
before all earlier recovery. The baseline and target are both FF. Unchanged
readback cannot prove write effectiveness. No CR1A/CR25/CR28/CR2D admission,
combined visible mode, native1.6 result, or Windows desktop result is implied.

See NEXT.md for current physical state. Build sources are frozen by sources001.
Private nxdk products remain under C:/xwn812/build002; not published.
Run restore_receipts001.py to restore/verify the exact large JSON host receipts
from lossless public text envelopes. This executes no guest or closed runtime.

Preserved failures:
- model002: stale guard comparison length after expanded result record. model003
  corrected only that comparison; 1,014 cases passed. model005 retains full820
  words for independent schema review.
- clock-model005: inherited stack offsets no longer match compiled main.obj.
  Disassembly showed1a80/1a84. clock-model006 uses those exact offsets; ten cases pass.
- review001 ran before model005 completed; missing receipt failure. review002
  ran after completion, passed source delta and complete schema/mutation checks.
- Initial git staging encountered ignored attribute/envelope files; these were
  explicitly staged. Qualified inherited CRLF/terminal blank line retained.

review003 is host qualification only. Physical launch/collection/audit records
must independently support any console claim. No source from a closed run was
executed unchanged or used as a runtime parent; reuse is pinned source-only.

Physical812 closed PASS: CR18 FF/FF/FF; seven logs, authenticated automatic return, audit002 PASS. No native or Windows claim.
