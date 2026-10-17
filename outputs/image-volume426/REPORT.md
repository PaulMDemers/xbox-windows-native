# 426: storage direction selected; host mapping contract passes

Selected a **fixed NTFS image stored as a normal FATX file** for the next
prototype. This preserves Windows names inside NTFS while retaining a FATX E
partition for the dashboard. It requires new loader and early block-device
integration; it is not currently bootable or a supported installation option.

The comparison in DESIGN.md reviews FATX creation, lookup/enumeration, rename,
deletion, FCB updates, file length, current loader NTFS/ARC boundaries, partition
mapping and install/recovery behavior. A logical-name FATX layer would require
a new durable namespace protocol across those paths. Unmodified old FATX drivers
would not honor its metadata protections. The fixed-image approach instead
keeps that namespace inside NTFS, at the cost of new boot/block ownership work
and loss of direct dashboard access to individual Windows files.

## Actual result

Original MIT host model, no guest or native build:

- tests001: **4,041 checks**. Every sector-aligned subrange of a fragmented
  seven-cluster example agrees with an independent sector-list oracle; absolute
  offsets remain above128 GiB. Also200 deterministic randomized fragmented maps,
  invalid geometry/chain/owner/bounds cases, descriptor publication/mutations,
  stale map/identity checks and partial-write/flush failure paths.
- tests002: **24 checks**. Independent byte-array writes leave every unrelated
  byte and final-cluster slack intact; the sector-aligned FATX format-size bound
  and lower read/write/flush exceptions are exercised.
- Incomplete IO and failed flush quarantine the model session while retaining
  its mapping. No false successful completion or modeled rollback is allowed.
- Descriptor checks reject every shorter prefix and every single-byte low-bit
  mutation of the example. A fresh external allocation map must match; saved
  physical offsets are never accepted by themselves.

**4,065 host checks total.** Ownership scans, identity, lower IO and flush are
explicit modeled inputs. No FAT parser, NTFS implementation, actual exclusion,
async IRP behavior, hardware flush, torn-data recovery or boot handoff is proved.
The canonical checksum is neither authentication nor an anti-rollback scheme.
Reusing a volume serial is not independently excluded by the model. The complete
identity and exclusion contract must be resolved before native implementation.

The model/tests are pinned in their receipts. source-review001.json records
current overlay hashes and the actual403 complete upstream directory reader;
the five reviewed full FATX source files match the recorded source tree. The
loader source review is not a claim of a newly compiled/qualified loader.
No test failures occurred in426. Preliminary read-only shell discovery included
an unsupported PowerShell brace glob and paths absent from the partial overlay;
those were corrected by enumerating the real paths and reading the full source.

## Unchanged boundaries

No physical access, no shared driver/SDK/source mutation, no installation,
no new emulator child, no deployment, no cleanup/offload or backing-chain move.
All commands completed; no owned running sessions. The original720p demo remains
restored, with no hardware test queued. All423/424/425 and earlier closed attempts
remain closed and their failed gates remain recorded.

C had21,320,617,984 bytes free at the initial capacity check, below the20GiB
build/launch reserve; E had21,732,130,816. Only lightweight Python host work was
done. No compiled build or guest launch bypassed the guard.

The six clean-install lossless-transfer exclusions, crypto failures on current
FATX, COM+ validation, strict events, installation/restore qualification and
1080i remain open. No Windows payload bundle or release tag is qualified by426.
See NEXT.md for the boot-device ownership discriminator before further coding.
