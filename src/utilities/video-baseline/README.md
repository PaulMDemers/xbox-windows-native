# XWN video baseline 680

This watched diagnostic requests **720×480×32 at 60 Hz through the running Xbox
kernel**. It does not run Windows or program the Xcalibur encoder directly. It is
preparation for a separate Xromwell 1.6 profile, not evidence that profile works.

It accepts only a reported HDTV AV pack, NTSC-M/J standard, enabled 480p and 64 MiB.
Other configurations produce a refusal record and return to the dashboard. It
does not change EEPROM settings to make a request eligible. The SDK's mode
selection forces progressive 480 under these conditions; the display's input
information and a watched image are still needed as physical evidence.

## Build

Use the installed nxdk environment described in the project build documentation.
Copy `main.c`, `pattern.h` and `Makefile` into a new short ASCII build directory,
then run:

```powershell
& C:\Homebrew\Invoke-Console.ps1 -Console xbox -WorkingDirectory C:\xwn-video-build -Command 'make -j4'
```

Use the project's build lease when sharing this workstation. Output is
`bin/default.xbe`. The reviewed local build's source and binary hashes are in
`outputs/revision680/builds001.json`. Later source changes require a new build
record; copying a historical executable is not rebuilding it.

## Watched run

1. Confirm the actual console revision, BIOS/mod, cable and dashboard 480p setting.
   Collect the ordinary hardware inventory first if this is a different unit.
2. Copy the XBE into a **new** `E:\Applications\XWNVideo680` directory after checking
   available space and reading the uploaded bytes back. Do not overwrite an
   existing installation. Do not add a startup hook or copy any Windows package.
3. Launch once while watching. Expected image: a white border; upper bars red,
   green, blue, cyan, magenta, yellow, white, black; lower horizontal stripes,
   vertical stripes, then checkerboard. Cells are eight pixels wide/high.
4. The image remains for approximately 20 seconds, then requests dashboard return.
   Observe colors, clipping, stability and display-reported input format. A
   successful API return alone does not establish those facts.
5. Collect the newly created `E:\xwn-video680-XX.json` records. They use exclusive
   creation, flush and readback; never overwrite older reports. Normal execution
   creates three records: `before_kernel_mode`, `pattern_submitted`, then
   `restart_requested`. Later records name their first record in `start_record`.
   `complete:true` means only that the application reached its restart request.
6. If it stays black or offline, report that state before resetting. This tool
   does not impose a timeout on kernel mode-setting calls and is **not an
   unattended probe**. A saved starting record may help locate the stop.

Only small report files are written to verified dashboard E. No network, EEPROM
write, disk identification, Windows startup change or dashboard C access occurs.
GPU observations are recorded for diagnosis; do not import them as programming
values for another console or bypass the framebuffer reservation contract.
