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

The private archives contain Windows/user material and must not be published.
They are not whole-disk images or necessarily the latest saved files. A specific
prepared E baseline has now passed a disposable offline installation, exact
partition restore and subsequent emulator boot/workload test. This does not
retroactively qualify other historical archives or prove physical-console
recovery. The emulator retained its Ftdisk 49 strict event failure.

## Offline E-partition recovery in a disposable image

`tools/xwn_image.py` is an offline Linux/WSL image tool. It accepts only a regular,
unmounted **10,000,000,000-byte raw image** with the standard E partition at
byte 2,884,108,288, length 5,120,024,576 and 16 KiB FATX clusters. It refuses
devices, symlink paths, custom partition tables and other geometries. It does
not connect to an Xbox, convert a QCOW image or modify a physical disk.

Stop the emulator and ensure nothing else uses the raw image. Use fresh output
directories and keep the backup outside the disk image:

```sh
python3 tools/xwn_image.py backup --image "$HOME/images/test.raw" --output "$HOME/backups/test-e-001"
python3 tools/xwn_image.py restore --image "$HOME/images/test.raw" --bundle "$HOME/backups/test-e-001" --output "$HOME/receipts/test-restore-001"
```

Backup reads E into `E.raw.gz`, verifies its decompressed hash, and records hashes
of both ranges outside E. Restore verifies the entire backup before writing,
requires those outside ranges to match, writes only E, then reads everything
back. Its `restore.json` distinguishes failure before writes from an interrupted
or failed restore. Never treat a started receipt as completion. Retain the
backup and failed receipt; use a fresh receipt directory for an intentional retry.

The image must still have a recognizable E header. This tool is not recovery for
an unreadable drive, damaged partition geometry or an unrelated console image.
It restores all of E, including saved data, to the backup's point in time. The
file lock coordinates cooperating processes; it cannot make a running emulator
safe to overwrite. A successful byte comparison is distinct from a subsequent
boot test and from physical-console recovery.
