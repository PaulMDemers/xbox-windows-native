# E demo menu installed; dashboard reload pending

The user reported a blank screen from the root Windows entry. The current menu
still targeted E:\Applications\XWNFBoot\default.xbe, the original F installation.
This confirms a stale target, not the cause of the old installation's blank screen.

After the user explicitly approved the narrow dashboard C exception, menu.py
changed only that item's Action to E:\Applications\XWNEBoot\default.xbe. The
current 1080i launcher and five E prerequisites matched the pinned policy before
the change. XML comparison and reversible byte comparison verified no unrelated
settings changed. The staged menu and installed menu were read back exactly.

Original configuration is preserved at /C/Dashboard/config.e380.bak and privately
at E:/xwn380/menu001/before.xml. Existing backups were untouched. No driver,
resolution, startup, F rollback or other C content changed. No console launch or
restart was sent. Reload UnleashX before testing the Windows entry; actual menu
boot remains unobserved. See installed.json for exact hashes and mutation receipt.

Demo378 was collected once beforehand. Its first-run log confirms outline applied
and saved; E drivers and original F rollback hashes remain unchanged. The user
reported the demo working very well, then requested full dragging and reported
poor text appearance. Current full-drag state and text cause remain unconfirmed.
Do not repeat the completed demo collection.
