# Exact dump-address loss localized

Crash005 is CLOSED and must never be relaunched or recollected. This was a
fresh unchanged-driver emulator diagnostic, not physical testing or ordinary
qualification. The user renewed authorization after the earlier cutoff; the
automation remains paused.

26 events and 43 resident byte pins prove the full first-write path:

* Kernel volume offset140436013056 plus partition offset8004132864 gives the
  correct disk offset148440145920. Division by512 yields sector289922160
  (`0x1147dc70`). The SRB/CDB and legacy routine's decoded LBA retain that value.
* Pinned atapi.sys dump writerRVA1360e callsRVA27fe directly. AtRVA28e7,
  `and al,0x0f` changes the high LBA byte from0x11 to0x01. The emitted sector
  becomes21486704, exactly128GiB lower.
* Device flags4262913 include the normal 48-bit capability bit0x400000.
  Command table bytes arec4c5ff2939, so an extended PIO write command is present.
  Actual cold registry already has EnableBigLba=1. Configuration is not absent.
* The legacy command selected is0xc5 atport1f7. All three ATA writes encode
  the wrong address; the writer returnsSTATUS_SUCCESS and final dump returnTRUE.
* Independent cold read finds the exactPAGEDUMP/cookie at11001192448 while the
  intended pagefile still startsPAGEPAGE. Dump qualification remainsFALSE;
  no recovery boot is allowed from this image.

All breakpoints were removed and the guest resumed before owned cleanup.
Allocation is consistent:324directories,6756files,325directoryclusters,
zeroerrors/orphans. Five hives parse and protected hashes match. These checks
are not an exhaustive statement that every file's content is unchanged.

Evidence: address-review.json, registry-state.json, address-verification.json,
verification.json, wire-verification.json and crash005/{trace,audit,closure}.json.
The original physical111-byte non-ASCII damage remains unexplained and separate.

Next: qualify the narrowly scoped private ATAPI selector correction using
matched ordinary runs, a new sacrificial high-LBA crash, and only after the
address/header gate passes, a separate recovery child. No physical deployment.
