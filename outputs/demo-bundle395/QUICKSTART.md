# Xbox Windows 2000 demo quick start

PREPARATION DRAFT:395 is held after physical394 failed. FATX390 has not been
accepted for the demo; the original0101 driver is restored. No395 ZIP exists.

For the configured console, no archive installation is needed.

1. Start at UnleashX. Keep the Razer keyboard unplugged through Xromwell.
2. Choose **Windows**. The direct fallback is `E:\Applications\XWNEBoot\default.xbe`.
3. Connect the keyboard after Windows appears. Close Welcome and any known
   unsupported-device prompts without disabling devices.
4. Use the desktop at **720p**. This is the mode where you confirmed clean text
   and full-window dragging. 1080i remains available for diagnosis, not the demo.
5. Try Notepad, Paint, Calculator, Solitaire, Pinball and audio. Save your work
   under Windows `C:\xwndemo372` and reopen it to check persistence.
6. Use **Start -> Shut Down -> Restart** to return to UnleashX normally.

## Dragging

Run `C:\xwndemo372\Full window dragging.cmd` or `Outline dragging.cmd`.
Changes apply immediately and persist for the current user. Use
`Display status.cmd` to inspect the setting. The supplied startup's one-time
outline default does not override an existing saved preference.

## Resolution

The preview's `docs/DISPLAY.md` includes exact host commands for inspect,
apply720p/apply1080i and restore. Set FTP credentials in the process environment.
The tool requires the console at UnleashX, checks the E installation, saves a
new rollback receipt and never boots the console. Do not use the older F tool.

## Files in this delivery

- **Preview ZIP:** demo controls, E resolution profiles/tool, tested FATX390,
  original0101 storage rollback, source/build references and instructions.
  The current console is already configured; no copying is required.
- **Private E-system ZIP:** reconstructed owned Windows/user payload for retention,
  not a fresh backup, empty-disk installer or tested full restore. Do not extract
  it over an occupied installation. Do not publish it.

Windows C is dashboard E; Windows F maps to dashboard C here. Keep dashboard C
and the original F Windows/loader rollback untouched. The existing Ftdisk49
warning and unsupported-device prompts remain documented limits. This is a
private experimental demo, not a new public release or full restore certification.
