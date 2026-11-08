# Selected project handoff, followed by full research-history staging

The user subsequently confirmed that C:, D:, and E: will all be wiped and
requested preservation of historical research on current disks for copying
off-machine. The original selected-save receipts below remain immutable.
The expanded handoff procedure is in [HISTORY-HANDOFF.md](../../docs/HISTORY-HANDOFF.md).
Its planned locations are the Desktop Save folder, D:/Save-Xbox-History, and
E:/Save-Xbox-History-E. The private final overview and manifests establish the
actual completion state; this source document does not certify an external copy.
The historical exclusion/undecided wording below describes the earlier stage.

## Original selected-save scope

On November 8, the user requested the final preservation set under
`C:/Users/Paul/Desktop/Save` before wiping the machine. Core files were copied
with source-change detection and an independent destination SHA-256 readback.
Source originals were retained. This is a selected project preservation set,
not a full disk or complete forensic-history backup.

The set includes both Windows 2000 discs, all three supplied RCT editions,
current private package inputs and five release packages, 845/846 console
preimages, older recovery material, firmware and distinct EEPROM fixtures,
photos, RCT saves/scenarios, the private installation answer image, and local
project skills/wrappers. It also retains two standalone stock emulator HDDs and
the complete header-declared 639-to-466 image chain with associated prerequisites.
The historical image chain remains closed evidence, not a new launch parent.
The EEPROM fixtures are not established physical-console recovery dumps.

Core receipt: 7,457 files. Additional receipt: 119 files. Source history, guides,
verification tools and final handoff metadata are saved separately. Exact hashes,
source paths, byte counts and final local verification are in the private Save
receipts and FINAL-STATUS.json, not in public Git.

The 130 GB environment backup and copied toolchains are excluded: use
[ENVIRONMENT-SETUP.md](../../docs/ENVIRONMENT-SETUP.md). Other historical raw disk
chains and the large D:/E: research archives are not copied in full. Their
retention/wipe scope has not been confirmed. Some unsaved chains reference C:.
See Save/NOT-SAVED.txt before erasing any old storage; this record does not
certify preservation of all historic raw evidence.

**Save is itself on C:. Transfer it to another physical disk and verify that
copy before wiping C:.** The standalone verifier reads only destination files
and receipts, so old source paths are not needed after transfer.

Tools:

- `tools/save-handoff.py`: explicit file plan, space reserve, no overwrites by
  default, copy/readback hashes, per-file receipt and failure retention.
- `tools/verify-handoff.py`: offline verification of complete receipts, file
  sizes and hashes, with path/reparse validation.
- `tests/test_handoff.py`: four synthetic tests passed, covering offline success,
  corruption/incomplete receipts, traversal and conflicting duplicate records.

No console or emulator was launched during this handoff.
