# Recovery and partition mapping

| Name | Meaning |
|---|---|
| Dashboard E | Current installation and `Applications\XWNEBoot` |
| Windows C | That same dashboard E installation |
| Dashboard F | Original installation kept as rollback |
| Dashboard C | Protected volume: no reads, listing, writes or cleanup |
| Windows F | Not dashboard F; the recorded capacity warning maps to dashboard C |

The repaired root Windows menu boots the current E demo through
`E:\Applications\XWNEBoot\default.xbe`. The separate original F rollback uses
`E:\Applications\XWNFBoot\default.xbe`.

Preserve bytes and hashes before replacing a launcher. Driver/registry changes
also require affected binaries, hives and startup files to be captured and the
expected baseline to match. Do not overwrite a newer installation with an old
whole recovery archive to undo one setting.

Undo outline dragging with `display-settings.exe full`. The deployment journal
preserves the old startup script; restoring it removes one-time initialization,
but does not reset the user preference. Change that through the tool or UI.

If a new profile fails, restore the captured E launcher from the dashboard.
Prefer Windows Restart while it responds. A forced reset can interrupt pending
filesystem writes and must be recorded.

Private256 recovery and E migration343 are distinct, readback-verified archives.
They are not whole-disk backups or proof of full restore testing. They include
owned Windows/user data and must not accompany public source releases.
Immutable 0.1.0/0.2.0 and original0088 remain unchanged.

## Storage-driver rollback for the399 demo

The tested390 driver is dashboard `E:\winnt\system32\drivers\xwnfatx.sys`,
SHA-256 `41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126`.
The preview's `rollback/xwnfatx-0101.sys` is the original driver,
SHA-256 `ba62acbb7dedf30154baba8d4cc2cf457f1a3e499bf7800e31011fba0e96d6a9`.
Both files are167827 bytes. Verify the hash, not just the size.

To undo only this change, return to UnleashX, preserve the installed driver's
bytes, then transfer the verified0101 file to that exact E path under the name
`xwnfatx.sys`. Download it again and compare its SHA-256 before booting. Do not
replace registry hives, user data or the whole installation for this rollback.
The existing private adoption receipt records the baseline and readback hashes.

The original driver retains the known duplicate-listing/CMD MOVE bug. Its
restoration/readback was exercised after physical398; that is narrower than a
full-system archive restore.399's reconstructed system ZIP is not a fresh backup.
