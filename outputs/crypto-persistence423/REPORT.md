# 423: two-boot NTFS security-state control completed

The original synthetic probe successfully creates and reopens user/machine RSA
keys and DPAPI blobs on the owned customized-SP4 NTFS installation. Both boots
have zero probe API failures. Each verifies saved signatures, freshly generated
signatures and exact decrypted bytes; the second boot verifies the same user SID.
All 41/42/43/69-byte direct filenames also survive. This is the NTFS control for
the next FATX comparison, not a FATX fix or public clean-install qualification.

Both unique boots are CLOSED with emulator exit 0, no deadline/host kill and
unchanged source disk/read-only floppy. Each cold event scan adds one shutdown,
one startup and one version record, with no new system warning/error. Event
record numbers put the shutdown before startup records, but generated times
put shutdown after startup; these are record scans, not rendered active-ring
qualification. Native restart requests and owned process exits are separate
supporting observations. No physical Xbox access occurred.

## Actual persistence evidence

The first run adds two RSA key files with 69-byte final components. The user
key uses the existing 44-byte SID directory. These are actual new API-created
paths, not a conclusion based only on old setup debris. Machine DPAPI creates
a new master-key file and Preferred under the short system SID directory.
User DPAPI uses existing profile state. Its two-boot success does not prove
that a new user master key was generated.

Cold inventories contain 6,475 files before, 6,491 after creation and 6,492 after
reopen; the last added file is reopen.log. Five hives parse after each boot and
all enumerated Windows EXE/DLL/SYS raw-reader hashes remain stable. Both QCOW
checks pass. The private final disk is under
`/home/paul/xbox-windows-native/crypto423-ntfs001`; never rerun either phase.
This is a new overlay continuation of the closed 404 clean installation, not
another install from ISO.

Independent NTFS-3G verification reads 41 final files, including both exact probe
logs, all retained crypto/protection files, five hives, provider DLLs and the
reader-discrepancy files. Both logs independently decode as complete with zero
API errors. All expected comparisons pass; the final disk remains unchanged.
See ntfs-independent001.json. This is selected independent content evidence,
not a full NTFS allocation-bitmap audit or COM+ test.

## Harness and reader findings

Two native executables build without warnings under the exact 403 compiler.
All 34/33 imports resolve against owned SP4 exports. Seven prior independently
extracted cold hashes agree, and 151 synthetic decoder checks pass. No binary,
private key, protection blob, hive, Windows DLL or credential is committed.

A full baseline comparison initially FAILED: 6,467 of 6,475 raw-reader files
matched the old 7-Zip manifest. Three event files have nonzero allocated bytes
beyond their 4,096-byte valid-data lengths; zeroing those uninitialized tails
matches the old extraction. Five compressed dllcache files differ in their
final compression unit. Independent NTFS-3G agrees with original 7-Zip on ALL
eight files. Thus the original extraction is corroborated; the new Dissect raw
reader is not a general logical-file oracle. Do not use its compressed-tail
bytes as replacement payloads or silently rewrite its failed comparison.

Pinned source inspection finds a relevant early break in the compressed-unit
reader before the following sparse run is examined when physical bytes equal
the remaining file length. The actual five differences start at the final
64-KiB unit boundary. This identifies the relevant parser path; no third-party
code patch or upstream fix is claimed. Event-log valid-data tails are a separate
semantic issue. compression-review001's misnamed raw_sha256 field hashes the
NTFS-3G reference file; preserve that field and interpret it explicitly.

Retained failures: first reader used the documentation's unavailable fs.get;
an audit lacked the Registry import path before reading; the initial stream
bound rejected the 44,033,096-byte driver.cab; a blank-password logon failed
before the fixture's saved logon was used; the eight-file raw comparison failed;
sudo kernel-device setup required authentication and made no attachment; package
symlink extraction on exFAT failed; the first independent reader used lower-case
paths that ntfscat did not resolve. All corrected executions use separate
records/outputs. No source disk was modified by these failures.

The unprivileged independent reader exposes one read-only NBD/FUSE file, not
an NTFS filesystem mount; both views were unmounted and subprocesses closed.
Private Dissect and libnbd/NTFS-3G tooling retains its upstream licenses.
See DESIGN.md and hashed dependency records; native witness code is MIT.

Three closed superseded emulator executables were ZIP-compressed, read back and
hashed on C before their originals were removed from E. The archives were then
copied/readback-verified on E and temporary copies removed. archive001.json
records restoration paths/hashes and 399,613,694 bytes reclaimed. No QCOW parent,
driver baseline, SDK or shared source was moved or removed.

Follow-up 424 is now CLOSED: the same binaries reproduce user RSA/user DPAPI
error 206 and machine RSA creation failure on FATX; machine DPAPI persists.
See [424's report](../crypto-fatx424/REPORT.md). Six existing filename exclusions,
inherited event failures, physical clean install/restore and public Windows-image
readiness remain unresolved. No previously frozen input was changed for follow-up.
