# Troubleshooting

| Symptom | First checks |
|---|---|
| Blank screen after choosing Windows | Confirm the menu points to the current E launcher, not an old F profile; inspect through the dashboard file explorer |
| Xromwell hangs before Windows | Disconnect the keyboard that caused prior boot hangs; keep the mouse connected before boot |
| No mouse after hot-plugging | Input discovery can be blocked by hardware setup; connect the mouse before the next boot |
| Found New Hardware wizards | Record the device name; cancel unsupported devices without disabling them |
| Broken-looking text or moving window contents at 1080i | Return to the matched 720p profile; this was clean in the user comparison |
| Normal text at rest but repaint visible while dragging | Try outline dragging; the desktop is software-rendered |
| Build refuses a changed hash | Inspect the source/tool difference; use explicit development mode for source edits, not an arbitrary compiler substitution |
| Build output directory already exists | Preserve its log and use a fresh attempt directory |
| Resolution selector refuses prerequisites | Stop and identify the installation/package mismatch; do not bypass hashes |

If Windows is responsive, save work and restart normally. If the dashboard is
offline, that alone does not prove a crash: Windows may simply still be running.
Record the actual screen and whether a restart was normal or forced.

For a useful issue report include console revision/encoder if known, RAM,
adapter and display, requested/observed mode, exact package or source tree,
last successful configuration, steps, and expected versus actual result.
Photographs and saved screenshots are different evidence; include both when
investigating presentation defects. Remove credentials, product keys, personal
files and console-specific secrets from logs before sharing.

The retained Ftdisk 49 event is a failed strict gate, not silently ignored because
the desktop works. Historical emulator dump-path fixes and the current physical
configuration are separate results. See [development](development.md).
