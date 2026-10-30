# Test842: USER-CONFIRMED WINDOWS 2000 DESKTOP ON XBOX1.6

User reports: "The system has settled on the windows 2000 desktop."
Recorded 2026-10-30T16:42:33.911550+00:00. Single physical desktop milestone, configured
fixed1280x720x32@60. Keep Windows running; do not power-cycle, relaunch, collect,
or resume the old automation. No hook or owned host runtime.842 is still open
at the desktop, not CLOSED. No normal Windows shutdown, cold persistence or
repeat-boot qualification yet. No desktop screenshot/mode query received.

841 had loaded VideoPort but never requested the miniport.842 restored the
existing Windows AGP bridge PCI initialization that retained-mode boot had
skipped. This13-write bridge block (including128MiB prefetch window and bridge
header/IRQ setup) was changed as a group; the result does not isolate one register.
GPU PCI setup and AGP reset stayed skipped; encoder/CRTC timing unchanged.
Existing miniport and ordinary startup unchanged. Existing FATX metadata-page
and root-chain repairs remain in the isolated loader driver. Clean baseline
SYSTEM was restored before launch; incomplete prior hives retained privately.

Working source/artifact/configuration pins: desktop-profile001.json and
launch-source-pins001.json. See REPORT.md, source001.json, stage001.json and
desktop001.json in outputs/boot720-bridge842. Preparation4cf51912 and single
accepted launch eb600852 pushed. Next validation, when user is ready: normal
Windows shutdown and authenticated dashboard, then one collection/cold audit.
Do not force shutdown or infer permission to interrupt this working desktop.
Reproduction must use a fresh owned attempt from pinned source/immutable inputs.
