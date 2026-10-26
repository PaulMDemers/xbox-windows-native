# 680 Networking parked; 1.6 video baseline prepared

The user has obtained a 1.6 Xbox and expects hardware access in a few hours.
Networking/timer testing is now tabled. `network-park001.json` pins retained
678/679 records and the private prepared executable. No old build was deleted,
restaged or launched. The 679 package is local-only and is **not queued**.
674's zero-datagram/lights-off observation still has no identified root cause.
The last known original-console state remains dashboard674; it was not polled.
No startup hook was added, and none was outstanding in the last verified state.

## Incoming-console preparation

The earlier inventory630 reports a user-identified 1.6,64MiB and kernel5838.
It does not positively identify Xcalibur: both older-encoder probes failed.
Whether the incoming unit is that console, its cable, BIOS/mod and current HD
settings remain pending. Historical free space is not a current capacity check.

The new [kernel-assisted utility](../../src/utilities/video-baseline/README.md)
requests720×480×32/60 through the Xbox kernel only when NTSC HDTV+480p and64MiB
are reported. It saves exclusive E-root JSON checkpoints, captures selected GPU
geometry registers and restores the CRTC index after its reads. It does not
read encoder registers or turn failed probes into an identification.

Expected display is a white border, eight color bars, and lower horizontal,
vertical and checkerboard panels. The pattern remains about20seconds, followed
by a restart request. Exact source/binary/package identities are in
`builds001.json`. Three successful build iterations are preserved; final003
adds observed-geometry validation and links later records to their start record.
The nxdk linker emitted its existing `.edata=.rdata` already-merged warning.
No shared SDK source or library was changed.

This is a **watched** diagnostic: kernel mode-setting is not bounded by the
application, and no emulator or physical execution of this XBE is claimed.
The compiled pattern helper was sanitizer-tested in681. Build success and model
tests are not visible-output proof. A20-second pattern fixes the too-short
observation window of earlier tests, not a proven display-driver defect.

The local ZIP is `C:/xwn680/package001/xwn-video-baseline680.zip`.
It contains the diagnostic and directions only, no Windows/RCT or firmware.
The existing Windows ZIP, ordinary720p path and private256 recovery are unchanged.
The experimental encoder work is recorded in [681](../xcal681/REPORT.md).

Next: [NEXT.md](NEXT.md).
