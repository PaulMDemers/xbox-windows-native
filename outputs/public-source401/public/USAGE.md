# Using the integrated demo

These instructions describe an already configured E installation. This source
package does not create one. Supply your own legally obtained Windows media;
no Windows or console firmware is included.

1. Connect the mouse before boot. Keep the Razer keyboard used in testing
   unplugged through Xromwell; connect it after Windows appears.
2. Choose the repaired Windows menu entry in UnleashX. It targets
   `/E/Applications/XWNEBoot/default.xbe`.
3. Use 720p for the demo. User observations report clean text and full-window
   dragging at 720p. The 1080i text gaps and motion artifacts remain unresolved.
4. Close unsupported hardware prompts without disabling devices. Use Notepad,
   Paint or the installed desktop applications. Save test documents in the
   Windows C drive's demo folder rather than an unfamiliar drive.
5. Use Windows Start > Shut Down > Restart to return to the dashboard.

The current startup is an ordinary desktop startup, without a timed test or
automatic restart. Outline dragging remains an optional preference:
`display-settings.exe outline`; compare with `display-settings.exe full`.

## Partition map and recovery

Dashboard E contains the current installation and appears as Windows C.
Dashboard F holds the older installation/rollback. Dashboard C is protected;
Windows F maps to that dashboard C and is not scratch space. Do not copy archives
over existing installations or replace hives wholesale. The private system bundle
is a historical reconstruction, not a fresh backup or a restore-tested image.

## Resolution selector

The included MIT `tools/configure-e-display.py` supports `inspect`, `apply` and
`restore`. Run it with `--help` before use. Its accompanying policy is pinned to
the existing E boot chain, miniport, boot-video and display binaries. It refuses
unrecognized prerequisites; a newly compiled binary will not automatically match.
No launcher binaries are distributed here. The older F-target selector is not
appropriate for the E installation.

Supply dashboard FTP host/user/password through `XWN_FTP_HOST`, `XWN_FTP_USER`
and `XWN_FTP_PASSWORD` in your local environment. Do not commit credentials or
save them in a public receipt. Start with an inspection and keep a private backup.
An apply stores the old launcher in a new receipt, writes only the E launcher,
verifies readback and attempts rollback on failure. It never starts the console.
Boot-time resolution changes require a subsequent normal boot; this is not live
mode switching. 1080i remains experimental even if the selector accepts its bytes.
