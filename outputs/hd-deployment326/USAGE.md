# Guarded 0.2.0 deployment tool

Run from this repository with Python3.14. Supply `XWN_FTP_HOST`, `XWN_FTP_USER` and `XWN_FTP_PASSWORD` in the process environment. The established hardware owner ticket must be active and all peer owners closed. This tool is for the known project console; it is not a universal installer.

Use a new private attempt directory for each deployment. It stores rollback binaries and must not be committed or published. Use a new receipt filename for every invocation.

```powershell
python -B tools/deploy-hd.py prepare --profile 1080i --archive D:/Codex-archive/xbox-windows-native/0.2.0/xwn-0.2.0-hd-overlay.zip --attempt D:/xwn-private/my-hd-attempt --receipt D:/xwn-private/prepare.json
python -B tools/deploy-hd.py apply --archive D:/Codex-archive/xbox-windows-native/0.2.0/xwn-0.2.0-hd-overlay.zip --attempt D:/xwn-private/my-hd-attempt --receipt D:/xwn-private/apply.json
```

Inspect the completed receipt and transaction state before booting. A prepared record is not an installed profile. The tool does not boot the console. Keep the Razer keyboard disconnected through Xromwell if manually launching the root Windows menu entry. The same method supports `--profile 720p` and `--profile baseline-restore`.

To put back the exact profile captured by that attempt, with Windows stopped and the dashboard available:

```powershell
python -B tools/deploy-hd.py restore --archive D:/Codex-archive/xbox-windows-native/0.2.0/xwn-0.2.0-hd-overlay.zip --attempt D:/xwn-private/my-hd-attempt --receipt D:/xwn-private/restore.json
```

Do not reuse these example paths after they have been consumed. Never rerun `apply` after a failed or committed attempt. A `quarantined` transaction means do not boot: preserve its journal and `unknown` captures and inspect the actual current bytes. Restoration accepts only known original/intended file states. A partially uploaded file or foreign change needs explicit recovery review; this tool does not guess ownership or overwrite it automatically. A crashed tool may leave its local lock; inspect the recorded owner before removing it.

No remote files outside the six display/boot paths can be written. All26 prerequisites are read and checked, including the shared HAL and unchanged startup. The original release instructions and known Ftdisk49 limitation still apply. A successful file round trip does not constitute a boot test, allocation audit, whole-disk restore, or proof of crash/power-loss recovery.
