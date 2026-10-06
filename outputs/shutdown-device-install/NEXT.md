# Gate before hardware installation

The baseline driver binaries are unchanged. A passing installed-state workload
is useful evidence for registration and repeated startup, but the first install
still recorded a shutdown popup and missed the dashboard return deadline.
Independent repeats do not resolve that first-install failure or qualify live
PnP removal, mode switching, or a replacement display driver.

Next experiment after these repeats: isolate first-time installation from the
workload. In a fresh copy of the failing rehearsal, use the same exact INF and
DevicePath edit, give the normal installer time to complete, then request normal
shutdown without the mapping workload. Preserve an unchanged control with the
same timing. Inspect SetupAPI, event deltas, exact binaries and cold registration;
do not set FAILEDINSTALL or suppress an installer. Vary one factor at a time.
This is a proposed experiment, not a recorded launch or result.

A hardware candidate requires a clean, reproducible installation/reboot path,
then matched display/GDI and persistence checks. Before deployment preserve and
hash the actual console's current files and relevant registry values, stage only
the intended package, retain normal startup and rollback, and verify readback.
Keep emulator-only PCI1B36:0005 support separate from physical Xbox devices.
Neither existing physical Srv2013 warnings nor the failed first installation is
waived by clean emulator replays. No new recovery snapshot or release is implied.
