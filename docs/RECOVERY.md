# Recovery and partition mapping

| Name | Meaning |
|---|---|
| Dashboard E | Current installation and `Applications\XWNEBoot` |
| Windows C | That same dashboard E installation |
| Dashboard F | Original installation kept as rollback |
| Dashboard C | Protected volume: no reads, listing, writes or cleanup |
| Windows F | Not dashboard F; the recorded capacity warning maps to dashboard C |

The root Windows menu boots F through
`E:\Applications\XWNFBoot\default.xbe`. The current demo boots E through
`E:\Applications\XWNEBoot\default.xbe`.

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
