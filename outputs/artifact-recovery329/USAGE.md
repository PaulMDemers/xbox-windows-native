# Recovered private 0.2.0 package on E:

Current package directory:
`E:/Codex-archive/xbox-windows-native/0.2.0-recovered329`.
The historical D: paths inside immutable release evidence are not current paths.
No D: drive is required. Original tags and historical reports remain unchanged.

`xwn-0.2.0-hd-overlay.zip` is byte-identical to the original release, SHA256
`474957aa6d2eb4cd8c3818a26ad0568e4b9c104b8159891c065b1491c8f6930d`.
The source/evidence ZIP also matches its original full hash. The combined
demo/recovery ZIP has identical uncompressed entries but different outer
packaging bytes. The regenerated history bundle contains the same immutable
release tags and complete history; its pack bytes need not match the old bundle.
Use the new recovery receipts and SHA256SUMS for those outer files.

This remains a private experimental upgrade for the tested Conexant console,
with boot-selected720p or1080i software video. Ftdisk49, unsupported-device
prompts, unconfirmed exact stereo routing, unproven repeated-boot reliability
and untested full-system restoration remain documented limitations. There is
no GPU acceleration or Windows dynamic mode switching. The physical console
has not been changed by reconstruction.

From the project repository, provide dashboard credentials through the existing
XWN_FTP_HOST/USER/PASSWORD environment variables and retain the hardware owner
ticket. Choose a fresh private attempt directory and fresh receipts:

```powershell
$overlay = 'E:/Codex-archive/xbox-windows-native/0.2.0-recovered329/xwn-0.2.0-hd-overlay.zip'
$attempt = 'E:/xwn-private/hd-install-unique'
python -B tools/deploy-hd.py prepare --profile 1080i --archive $overlay --attempt $attempt --receipt E:/xwn-private/prepare-unique.json
python -B tools/deploy-hd.py apply --archive $overlay --attempt $attempt --receipt E:/xwn-private/apply-unique.json
```

The tool checks all26 prerequisites, saves rollback bytes, installs all six
matching files with readback, and installs the launcher last. It never boots.
Only after a completed apply receipt, launch the root Windows menu in UnleashX.
Keep the Razer keyboard unplugged through Xromwell. Return through Windows
Start → Shut Down → Restart. Use `--profile 720p` at prepare for720p instead.

To restore exactly what that attempt captured, while back at the dashboard:

```powershell
python -B tools/deploy-hd.py restore --archive $overlay --attempt $attempt --receipt E:/xwn-private/restore-unique.json
```

Never repeat an accepted/failed apply or reuse consumed attempt paths. A
quarantined receipt requires inspecting its preserved current bytes; do not
boot or guess a rollback. Read outputs/hd-deployment326/USAGE.md for transaction
details, substituting these current E: paths for historical examples.

The combined private-demo archive contains the original256 system and boot
recovery ZIPs. Keep them private; they contain owned system/user files. They
are not a whole-disk image or a tested bare-metal installer. Do not unpack them
over an existing installation without reviewing paths and preserving user data.
