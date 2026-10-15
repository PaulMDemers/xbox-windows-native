# Clean Windows media validation (404)

The supplied customized OEM-channel disc completed a new blank-disk PC setup,
first logon, normal shutdown, then a media-detached desktop boot and second
normal shutdown. This is a scoped PC installation pass, not a fresh Xbox assembly
or fully unattended harness pass. No physical console was accessed.

The retail disc's fresh setup remains pending a matching retail key. A private
file path was requested; no online key was used. Its integrity checks passed.

## Disc identities and online comparison

| Disc | Bytes | SHA-256 |
|---|---:|---|
| Retail SP4 | 386859008 | e3816f6e80b66ff686ead03eeafffe9daf020a5e4717b8bd4736b7c51733ba22 |
| Customized OEM-channel | 594280448 | 75ae5e4980e074377d3f0c2ab2e82dff0e3f80400da13c8e2d5a1479d2ccda1f |

Full Archive.org downloads and a second readback matched each supplied ISO in
size/SHA-256/SHA-1. These are exact third-party copies, not proof of Microsoft
authenticity. Both ISO files were parsed and every file read: 6157 retail files,
6806 customized files. Their DRIVER.CAB, SP4.CAB and compressed kernel completely
decompressed. The actual extracted kernels are 2195.6717 and 2195.7376 respectively.
The twelve current input-component provenance results remain those of403.

See online-retail001.json, online-customized001.json, media-structure001.json and
upstream/windows-media.json. The extra retail mirror was catalog-only; a third
customized disc had a different SHA-1 and was not downloaded/qualified. Official
Microsoft sources found were updates, not a verified full installation ISO.
Public source links and distinctions are in docs/windows-media.md.

After a further comparison with the preserved supplied originals, the two
redundant downloaded copies were removed, recovering981139456bytes onC. Receipts
remain; neither supplied ISO was changed. See duplicate-download-cleanup001.json.

## Actual PC sequence

Fresh2GiB QCOW2 with no backing image,64MiB PentiumIII/IDE/Cirrus, QEMU10.2.1,
no network adapter or shared Windows tree. The read-only private answer floppy
used only this supplied disc's embedded OEM key. OemPreinstall=No excludes optional
OEM post-commands. Firmware/emulator/probe/media hashes are recorded. The witness
was compiled from original source with the fresh403 RosBE receipt, not downloaded.

1. Phase1 text setup completed and requested its reboot.
2. Phase2 GUI setup completed16:52:01UTC and requested its reboot.
3. Phase3 first logon ran A:\PROBE.EXE, recorded completed setup and accepted
   shutdown. Guest exited16:53:13UTC without host termination.
4. Phase4 started16:57:51UTC with neither CD nor floppy attached. The desktop
   appeared. RunOnce had been removed after first setup: the witness did not
   automatically launch. It was started once through the normal Windows Run
   dialog after closing Welcome. It confirmed CD unreadable/setupcomplete and
   requested shutdown; guest exited17:01:04UTC without host termination.

All four phases exited0 without deadline, reset, forced quit or kill. First and
final cold evidence shows1 then2 normal shutdown records, no warning/error or
application records, exact kernel7376 matching the ISO, both witness files and
the unchanged compiled probe. Five hive headers/sequences are clean at both
boundaries; every key and declared raw value agrees between independent readers.
QCOW checks pass. These are selected-file/registry checks, not a complete NTFS
allocation/file-content safety audit. The final disk is preserved privately at
/home/paul/xbox-windows-native/clean-media404-oem001/disk.qcow2.

## Retained failures and corrections

- Probe001 link failed on memset;002 uses a volatile explicit zeroing loop.
  Only002 was run. Its imports are kernel32/user32/advapi32, subsystem5.0.
- Initial cold auditor failed typed decoding of SOFTWARE/Microsoft/DRM/DataPath,
  type0x404. Its raw80bytes remain uninterpreted. No registry was repaired.
- Reader comparison002 initially compared Python Registry's interpreted inline
  string/MULTI_SZ bytes against hivex's declared raw bytes. Actual library source
  demonstrated the difference. Bounded VK raw reader004 uses declared lengths;
  every stored type/byte agrees with hivex. Ten boundary controls pass. The
  original typed-decoder failure remains a strict failure, not silently waived.
- Diagnostic003 printed SYSTEM/SOFTWARE differences but then used lower-case
  sam on a case-sensitive extracted filesystem; its failure/source remain.
- Phase4's conservative22.5GiB preflight refused before extraction. Replacement005
  still reserves20GiB, plus all actual mapped data extents and256MiB for selected
  extraction/metadata. Explicit sparse conversion and actual allocation/budget
  checks passed. WSL raw deletion had not immediately returned host capacity.
- The automatic RunOnce handoff failed. Manual ordinary GUI invocation is
  explicitly recorded; no fully unattended result is claimed.
- A late phase3 screenshot request found the guest had already exited. No
  relaunch followed. A PowerShell inline generator quoting error occurred before
  creating the source-package script; the corrected literal-input generator ran.

Full typed decoding and automatic handoff remain false. The scoped PC pass is
reported separately. Windows' existing Xbox Ftdisk49 failure is a different test
and has not been changed or waived.

## Public tooling and checks

tools/verify-media.py reads size/SHA-256/SHA-1 and reports the manifest's recorded
scope; recognition cannot upgrade a pending installation. Four focused tests
pass. All27 public-tool tests pass on Linux; Windows run passed18 with9 explicit
platform skips. Thirteen synthetic qualification negatives, ten raw-value
boundary checks and seven mutations of actual cold reports reject bad states.

New public guide/manifest and updated build/provenance/install/validation links
are in the private535-entry source review ZIP; every entry read back, repeat ZIP
byte-identical. No ISO, key, hive, firmware, Windows binary, private history or
runtime screenshot is included. This is a private review artifact, not publication
or a release tag. See source-package003.json for its exact SHA-256. The first
two bundles remain intact.002 followed canonical LF normalization of the new
public manifest; index review then found three inherited working JSON files
with CRLF versus staged LF. Their values are identical.003 packages exact staged
bytes and is checked against the index, without altering historical evidence.
