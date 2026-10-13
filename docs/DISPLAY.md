# Display configuration

Resolution is boot-selected. Windows Display Properties is not a supported way
to switch these profiles while Windows runs.

| Installation | Launcher directory | Evidence |
|---|---|---|
| Current E demo | `E:\Applications\XWNEBoot` | Physical 1080i; E 720p under qualification |
| Original F | `E:\Applications\XWNFBoot` | Older private 0.2.0 720p/1080i and original rollback |

These paths select different Windows installations. The old `tools/deploy-hd.py`
targets F even though its launcher is on dashboard E. Do not use it for E.

## Choosing a mode

720p carries about 44% as many pixels as 1080i (1280×720 versus 1920×1080).
That is a pixel-count comparison, not a measured speedup. 1080i provides a larger
desktop; fine horizontal details may flicker on an interlaced display.

The tested console has a Conexant encoder and an HD-capable signal path. An HDMI
connector alone does not establish adapter compatibility. Other encoders,
adapters and TVs need their own checks.

## Safe changes

1. Save work and restart into UnleashX.
2. Verify the package names the E installation and matches its installed
   loader, miniport and display prerequisites.
3. Preserve the current launcher bytes and SHA-256.
4. Apply the selected E profile and verify readback. Do not mix F loaders or an
   older framebuffer reservation into this chain.
5. Boot once; check actual Windows dimensions, TV signal, border, colors and
   stability. Record what was observed rather than assuming the requested mode.
6. On failure, return to UnleashX and restore the captured launcher. Retain F.

No mode change edits dashboard C or EEPROM flags. The E 720p launcher uses the
original720p source with only its loader path changed. Its emulator result is
recorded in377; physical qualification on the E installation remains pending.

## E selector in the demo preview bundle

Run from the extracted preview bundle on the development PC, with the console
at UnleashX. Supply FTP credentials through `XWN_FTP_HOST`, `XWN_FTP_USER` and
`XWN_FTP_PASSWORD` in that process's environment; do not save them in the repo.

```powershell
python tools/configure-e-display.py inspect --policy tools/e-display-policy.json
python tools/configure-e-display.py apply --policy tools/e-display-policy.json --profile 720p --launcher resolution/720p/default.xbe --receipt rollback-720p-001
```

The receipt directory must be new. To return to the exact captured profile:

```powershell
python tools/configure-e-display.py restore --policy tools/e-display-policy.json --receipt rollback-720p-001
```

To explicitly select1080i, use `--profile 1080i --launcher
resolution/1080i/default.xbe` with a fresh receipt. The selector checks the five
shared prerequisites, preserves the current launcher, changes only the E
launcher and verifies readback. It never starts Windows. Boot the E launcher
yourself afterward. Keep the receipt until the new mode is checked.

If rollback cannot reconnect or the current launcher is unrecognized after an
interrupted transfer, preserve the receipt and restore its verified `before.xbe`
to the exact `E:\Applications\XWNEBoot\default.xbe` path using dashboard FTP.
Do not substitute files from the F profile. No signal during Xromwell requires
returning to the dashboard before this recovery can run.

## Outline dragging

Run **Outline dragging.cmd**, or:

```bat
C:\xwndemo372\display-settings.exe outline
```

Use `full` to undo and `status` to inspect. The utility uses the Windows
system-parameters API and verifies the saved preference after a change. It does
not edit driver, GPU, cache, PTE or MTRR state.
