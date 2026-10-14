# Recovery and rollback

Preserve a working dashboard, original launchers, matching loader/driver bytes,
console-specific recovery material and your own saved files before updates.
Record hashes and partition names; do not assume Windows and dashboard letters
match. On the current E demo, Windows F maps to dashboard C and is not scratch.

## Display rollback

Return to UnleashX and use the display selector's captured receipt to restore
its previous launcher. If an interrupted upload leaves an unrecognized launcher,
preserve the receipt and restore its verified `before.xbe` to the receipt's
exact E launcher target through dashboard FTP. Do not substitute an F launcher.
A no-signal Windows boot must return to the dashboard before this recovery works.

## Driver or installation rollback

Use the exact previous files for the same installation, with upload/readback
verification. Preserve the original F installation separately from E. Do not
restore a private system archive over an occupied installation as an upgrade.
Restore user data only after confirming the destination mapping.

The project's private recovery archives were readback-verified, but are not
whole-disk images and have not passed a full-system restore test. They contain
historical Windows/user material, not necessarily the latest saved files, and
must not be published. Archive integrity is not proof of successful recovery.
A disposable install-and-restore test remains a public release prerequisite.
