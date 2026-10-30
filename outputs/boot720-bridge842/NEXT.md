# Test842 closed: desktop confirmed; mouse hot-plug did not work

The user reached the Windows 2000 desktop on the physical 1.6, reported no response from a mouse plugged in after boot, and returned to UnleashX without a clean Windows shutdown. Dashboard authenticated, no hook, one collection and cold audit. Do not relaunch, recollect, or use the runtime as a parent.

The Windows miniport trace changed from baseline: 44 events, zero lost, successful framebuffer acquisition at physical 0x03700000. This corroborates the Windows display path, not an independent mode query. The new SetupAPI tail records one OpenHCD controller completing install and another starting interface installation; it contains no mouse/HID install. This does not identify the cause of missing input. The five primary hives and relevant logs were preserved privately; none of their headers declares missing file bytes. Clean shutdown/persistence is unqualified.

See closed001.json, input-video-cold001.json, hive-length001.json, collection001.json and audit001.json. Follow outputs/boot720-input843/NEXT.md.

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

842 screen requested after >2min. Dashboard poll001 timed out; Windows result unknown. Await user screen; no launch or collection. Use physical003.py. No hook or owned host runtime. Preparation4cf51912 and launch eb600852 pushed.

# Test842 launched once; awaiting Windows screen

SITE accepted at 2026-10-30T16:35:30.214789+00:00. No retry. Use physical003.py ONLY.
Fixed720p retained; existing Windows AGP bridge initialization restored and
critical window/bus/IRQ readback required before Windows. GPU PCI setup and
AGP reset remain skipped; no encoder/CRTC timing change. Display miniport
unchanged. Fresh SYSTEM baseline restored with exact readback. Source-only
reuse, no failed runtime parent. Preparation4cf51912 pushed. No hook or owned
host runtime; all CPU fixtures closed. Old automation remains paused.

After2min obtain screen. If desktop leave running. If blue photograph LOAD842
and XWN842; if loader text capture it. Capture evidence before user power off/on,
then authenticate dashboard and collect842 once. No dashboard return assumed.
841 CLOSED: VideoPort loaded, no observed miniport request; no relaunch or
recollection. Direct user request remains Windows desktop at fixed720p.

# Test842 qualified: restored Windows AGP bridge setup, fixed720p retained

841 CLOSED: VideoPort loaded, no miniport open/read/image notification. Existing
Windows binding remains intact.840 kernel inventory showed64MiB bridge prefetch
window; existing Windows GPU resource record/working trace uses128MiB. Retained
boot had skipped the whole normal bridge initializer.842 re-enables its exact
existing13 PCI writes, all to00:1e.0; GPU PCI initialization and AGP reset remain
excluded. Critical window/bus/IRQ readback must pass before Windows starts.
No encoder/CRTC timing change. Miniport unchanged. This is not yet a proven fix.

Host exact bridge block20cases, observer21cases, cache62cases, retention/map,
imports/residency, copy/allocation and13 diskless CPU cases passed. All CPU
fixtures closed. Source-only reuse from841 with pins, no failed runtime parent.
SYSTEM restored from immutable package after preserving incomplete841 hive;
exact readback verified. An initial restoration-helper import failure occurred
before hardware access and is retained. Use restore-system002.py if reviewing.

Next unique E:/Applications/XWN16Boot842 stage/readback, commit/push, one SITE20s
via physical003.py. After2min obtain screen; if desktop leave it running. If
blue, capture LOAD842/XWN842, then user power off/on and authenticate dashboard
before one collection/audit. No hook or owned host runtime. Ordinary startup
unchanged; old automation paused; direct user desktop work active.
