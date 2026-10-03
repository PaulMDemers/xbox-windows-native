# XWN hardware probe v2

This revision fixes a physical-console hang in v1. Use this package for the next test.

1. Extract `XWNProbe2` from `xwn-hardware-probe-v2.zip` and copy that folder into `E:\Apps` on the Xbox.
2. Launch `E:\Apps\XWNProbe2\default.xbe` from UnleashX. It should show a v2 heading, PCI progress, then a saved-report message.
3. After completion, reboot to UnleashX and retrieve `E:\Apps\XWNProbe2\xwn-hardware-v2.txt`.
4. If it stalls, restart as before and retrieve that same file. Its last BEGIN/END marker will narrow down the failed step. If no file exists, report that instead.

Keep v1's report for comparison, but do not run the v1 XBE again. This package uses a new folder and filename. It does not boot Windows, change partitions, issue ATA commands, or access EEPROM secrets. It initializes the display and writes the app-local report.

## What went wrong

The physical v1 report ends after PCI 00:00.0. The next operation in v1 was a read of 00:00.1. ReactOS's [Xbox PCI implementation](https://github.com/reactos/reactos/blob/master/hal/halx86/legacy/bus/pcibus.c) explicitly excludes 00:00.1 and 00:00.2 because they can hang an Xbox. The observed stopping point strongly matches this documented hardware issue. It is not a trace proving the precise stalled instruction.

V1 initialized video but printed its screen summary only after the scan, so a scan hang left no visible progress. V2 prints before scanning, reads only twelve explicit targets, blocks the dangerous host functions and GPU aliases, and flushes the log before every hardware read. It also logs before video initialization. The target addresses follow the [Xbox hardware inventory](https://xboxdevwiki.net/Xbox_Hardware_Overview); the unused modem and additional optional devices are deliberately omitted.

The physical report confirms kernel 1.0.4034.1, 16,384 physical pages (64 MiB), GPU revision 163, MCPX revision 178, ELCR 0x1800 and raw encoder settings 0x004f0101. It does not establish an exact motherboard revision or successful display output. See `evidence/physical-v1-incomplete.txt`.

## Validation

The source builds against the installed nxdk commit 58427c078b4ccb0121f359b6b6c536b3b2914976. The host C test checks all 65,536 bus/device/function combinations, allows twelve distinct targets, and rejects the dangerous functions and GPU aliases. This verifies the address policy; xemu alone cannot validate the hardware-specific hang fix. Emulator run hardware-probe-005 tests the XBE launched from a private UnleashX FATX directory; its captured screen and extracted report are under `evidence/`. Physical v2 validation is pending.

Rebuild with `Invoke-Build.ps1` from PowerShell 7.4. The shared console launcher/build lease is used; intermediate files stay under `work/hardware-probe-v2-build`. See `manifest.json` for source and binary hashes. No additional ISO is required for the console test.
