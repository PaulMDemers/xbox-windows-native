# Private stock-E 1080i migration bundle

This bundle reconstructs the exact 6,566-file E payload tested by physical342. It is a private same-console migration from the captured F installation, not a generic Windows installer for a fresh Xbox. It includes owned Windows files and registry hives; keep it private. The new installer requires this repository, the active demo251 hardware ticket, the owned F marker, and the exact original F rollback files. It cannot provision a console without that baseline.

The installed Xbox already has this payload. **Do not reinstall it.** At UnleashX, use the file manager to launch `E:\Applications\XWNEBoot\default.xbe`. Leave the keyboard unplugged through Xromwell. The existing root Windows menu still launches the original F installation. For rollback, use `E:\Applications\XWNFBoot\default.xbe`; this bundle never rewrites that launcher or the dashboard menu on C.

The tested profile is software-rendered 1920x1080, interlaced output, on the tested Conexant console and adapter. It is not accelerated or a dynamic mode selector. Physical342 passed drawing, audio API, normal shutdown and integrity checks. Its combined event gate failed on Srv2013 (a Windows letter mapping to dashboard C); strict qualification also failed on Ftdisk49. These failures remain. No C capacity query, cleanup, or event suppression is part of this package. There is no new release tag.

## Verify the private archive

From the reviewed repository checkout, use Python 3:

```powershell
python -B tools/install-stock-e.py verify --profile stock-e-1080i --archive E:/xwn343/bundle001/stock-e-1080i-001.zip
```

This verifies the pinned manifest, exact entry set, and every payload/support hash without console access. `tools/stock-e-profile.json` is the external manifest pin. The archive includes the complete create-only install plan, seven original changed-file preimages, the capacity probe, instructions and source tools. Tools inside the ZIP are source copies, not a standalone executable installer; use the matching checkout and its physical ownership dependencies.

## A future vacant-target migration on this owned console

The four target directories must all be absent: `E:\winnt`, `E:\documents and settings`, `E:\program files`, and `E:\Applications\XWNEBoot`. Existing content causes refusal; the tool has no overwrite, removal, repair or resume mode. Do not delete the current installation to exercise this procedure. E Apps and the F rollback are preserved. No Games cleanup is needed for this installation.

Set `XWN_FTP_HOST`, `XWN_FTP_USER`, and `XWN_FTP_PASSWORD` in the process environment using the console's credentials. Keep the console at UnleashX and other hardware clients idle. Use a fresh private attempt directory:

```powershell
python -B tools/install-stock-e.py prepare --profile stock-e-1080i --archive E:/xwn343/bundle001/stock-e-1080i-001.zip --attempt E:/xwn343/install-new-unique
python -B tools/install-stock-e.py install --profile stock-e-1080i --archive E:/xwn343/bundle001/stock-e-1080i-001.zip --attempt E:/xwn343/install-new-unique
```

Preparation checks vacancy and the original rollback first, then writes and launches ONE uniquely named native capacity probe under E Applications. It waits at most five minutes for its dashboard return. It does not launch Windows. Installation must start within ten minutes of the capacity result and requires the reviewed standard E geometry plus payload allocation and 256 MiB reserve. It consumes the preparation once, creates files with full readback and an fsynced journal, and writes the new launcher last. The upload budget is two hours. FTP does not provide an atomic create-only transaction; exclusive ownership is required throughout.

If any stage fails, preserve `transaction.json`, `writes.jsonl`, and the capacity report. Do not rerun a failed or consumed attempt, boot an incomplete payload, or manually remove partial files. Inspect the exact journal against the complete install plan before designing a separate recovery. Post-install allocation and boot qualification are separate required steps; a successful upload alone is not a release qualification. The generic create-only installer is host-tested; the current physical installation was performed by the separately preserved340 staging/recovery controllers.

## Reconstruct the payload

Use the owned337 capture, recovered immutable0.2.0 HD ZIP, and reviewed334 E boot outputs. `tools/package-stock-e.py` takes explicit `--capture-root`, `--hd-archive`, `--boot-root`, unique `--output` and `--receipt` paths, plus `--profile stock-e-1080i`. Run it in the existing WSL offline-hive environment with hivex and `nt5_hive_indexes.py`. It verifies all source bytes, changes only four MountedDevices values semantically, installs the three reviewed HD files and three E boot files, and retains normal startup. It does not compile the SDK or drivers. Two independent payload reconstructions and two deterministic ZIP assemblies are recorded in assembly001.json. Do not rerun consumed evidence IDs; use new output paths for a future reconstruction.
