# 0.1.0 recovery and provenance

Use `capture.py` only against the owned console and an idle Windows installation.
It refuses mismatched baseline drivers/loader/startup and requires the existing
deployment ownership marker. Supply the FTP password through XWN_FTP_PASSWORD;
it is never saved in source or reports. A completed capture is not an installer.

The archive directory contains `capture-manifest.json`, `physical-files`, two
ZIPs, and later a source archive/Git bundle. Each manifest entry is a dashboard
FTP path, byte length and SHA-256. `F/winnt` maps back to dashboard F:\winnt,
not dashboard C:. `E/Applications/XWNFBoot` is the independent launch chain.
The saved profiles include the user's Paint pictures and registry state: keep
the system archive private. Check capture-summary.json and the local manifest
before trusting any recovery copy.

For a future recovery, first remain in UnleashX and preserve the failed files,
logs and current directory metadata. Compare file hashes and choose the smallest
repair set. Do not format or repartition, restore an entire disk from this
file-level snapshot, or overwrite unrelated F: contents. Restore files to the
same owned paths only after verifying the physical partition and marker. Never
substitute the emulator HAL or synthetic PCI fixture for the physical HAL.

Restoring the installation broadly requires an explicit restore plan, free-space
check, FATX path validation and quiescent Windows. The snapshot omits pagefile.sys;
its runtime contents are not needed as recovery data, but pagefile recreation
must be checked on a restored system. Keep no-op startup disabled until file,
allocation and hive checks pass. Then perform one normal boot/restart and cold
integrity check. A full recovery rehearsal has not been performed for 0.1.0.

The menu change preserves the old config both locally and under a unique remote
backup name. Restore that exact file to its recorded config path if needed;
do not replace the dashboard executable or the softmod boot chain. Dashboard C:
may be a shadow mapping. A visible config write/readback is not proof of raw-C
identity or persistence across a softmod reset. Confirm the Windows entry after
the next ordinary dashboard reload; do not change EEPROM/softmod settings.

Private Git stores source patches, test code and reviewed reports. The tag is
`v0.1.0`; use the companion source manifest's revision and hashes for archives.
The upstream ReactOS/Cromwell versions and build commands remain in the pinned
source locks and component build reports. See NOTICE.md for licensing/provenance.
