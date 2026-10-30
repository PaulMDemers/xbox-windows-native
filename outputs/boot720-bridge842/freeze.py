"""Freeze qualified842 fixed720p Windows boot with restored AGP bridge setup."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-load841'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=['source001','baseline001','bridge001','load-host003','driver003','driver-host002','driver-review002','qualify002','chain002','host007','cpu-build011','cpu-run011','build003','restore-system001']
for n in records[2:-1]:assert read(K/(n+'.json'))['passed']
assert read(K/'restore-system001.json')['completed'] and read(K/'cpu-run011.json')['closed']
for key in ['retention_unchanged_sha256','loader_fat_unchanged_sha256']:assert read(K/'source001.json')[key]==read(A/'source002.json')[key]
pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.c','.h','.S','.ld','.patch'] or p.name in ['Makefile','.gitattributes']+[n+'.json' for n in records])}
out=K/'launch-source-pins001.json';assert not out.exists();out.write_text(json.dumps(pins,indent=2)+'\n')
note='''# Test842 qualified: restored Windows AGP bridge setup, fixed720p retained

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
'''
(K/'NEXT.md').write_text(note)
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:p.write_bytes(note.encode()+b'\n'+p.read_bytes())
print('842 exact inputs frozen; no launch requested')
