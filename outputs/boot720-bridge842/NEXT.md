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
