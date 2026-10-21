# Windows 480p validation prepared; no boot result yet

The unchanged633 candidate is ready for a Windows-level test. A fresh overlay
uses the never-executed466 seed (SHA2567709d6ac9867cb842c2f95f3478fced69f106fad5d199abebf004d464c4c2670).
The ordinary720p launcher remains present and unchanged. A separate owned
`Applications/XWN480p634` launcher and `xwn480p634` probe are staged in the
private fixture. No physical console files were accessed or changed.

Probe build002 is19405 bytes, SHA256
49600b8f0bd9326e22ceec334ee458d47ca9e7c31096a9fe2e5e9a6374e78976.
The pinned RosBE compiler built it without warnings. PE32 subsystem5.0 and
all imports were checked against the actual fixture's NT5 DLL exports.
The probe reports current mode and screen metrics, locks the DirectDraw primary
surface read-only to report pitch, checks full-window GDI upload/readback and
overlapping copies in both directions, then requests a normal restart without
forcing applications closed. It logs failures as well as completion.
API acceptance alone will not establish restart or persistence.

Preparation passed byte readback, unchanged five hives/protected files and full
FATX allocation checks:277 directories,6555 files,zero orphans/errors.
Independent snapshot-based oracle review checked691200 pixel values and rejected
14 corruption/omitted-copy/wrong-traversal cases. These are host mathematics,
not evidence that GDI, DirectDraw, Windows, or physical480p worked.

The final projected-space check refused the launch before any runner or instance
receipt. **634emu001 remains prepared and never launched.** No observed desktop,
pixel result, primary pitch, shutdown event, or runtime disk mutation exists.
The192MiB allowance covers up to128MiB overlay growth,32MiB capture/logs and32MiB
buffer; the controller also checks remaining free space and artifact growth.
C subsequently fell below the20GiB reserve. A user capacity question is pending.
Do not lower the reserve or run a guest without the projected allowance.

Preserved failures: first read-only inventory expected a startup file absent
from this seed; build001 failed to link memset; build002 supplies a small local
implementation. The failed build source remains in private build001, with its
hash and linker output retained in public build001.json. Space refusal001 is
separate from a boot failure. No guest runtime was consumed.

Capacity work moved one compressed closed561 archive byte-exactly to E:
see archive-relocation001.json. Original disk bytes remain recoverable with the
same checksum; no executable disk or backing chain was moved. Existing emulator
and media duplicates were already hardlinked and were not deleted. Delivery587
ZIPs had already been reclaimed in589, so no new reclamation was counted.

The633 native-initialization result and limitations remain unchanged, including
its preserved reserved-sector equality failure. No new hardware qualification,
live Windows switching, acceleration, additional-revision support, or release
promotion is claimed.

## Completed runtime

Read final-review001.json and audit001.json: the previously blocked fixture ran
once and is now CLOSED. Actual720x480x32/60Hz, all three GDI checks and normal
restart passed their observations, with intact protected files/hives/allocation.
Complete probe FAILED: primary Lock returned DDERR_CANTLOCKSURFACE0x887601b3,
so no primary pitch was obtained. Strict events retain Ftdisk49 and Removable
Storage Service116. Login required the retained installation credentials after
a rejected blank login. Unsupported HMP screenshots and observer/hive-reader
issues are preserved. No physical test or release qualification follows.
