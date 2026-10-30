"""Freeze exact841 preparation, including clean SYSTEM restoration."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-rootchain839'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=['source001','baseline001','load-host002','driver002','driver-host002','driver-review001','qualify002','chain002','host006','cpu-build010','cpu-run010','build002','restore-system001']
for n in records[2:-1]:assert read(K/(n+'.json'))['passed']
assert read(K/'restore-system001.json')['completed'] and read(K/'cpu-run010.json')['closed']
for key in ['retention_unchanged_sha256','loader_fat_unchanged_sha256']:assert read(K/'source001.json')[key]==read(A/'source001.json')[key]
pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.c','.h','.S','.ld','.patch'] or p.name in ['Makefile','.gitattributes']+[n+'.json' for n in records])}
out=K/'launch-source-pins001.json';assert not out.exists();out.write_text(json.dumps(pins,indent=2)+'\n')
note='''# Test841 qualified: observe display image loading during fixed720p boot

839 CLOSED B4;840 read-only PCI inventory CLOSED after automatic dashboard
return. Fresh841 retains720p and prior functional FATX repairs. Adds only RAM
observation of display image opens, reads, EOF byte and kernel-image notifications.
No miniport, PCI, timing or encoder change. Display driver remains installed
baseline. Clean immutable SYSTEM restored after private839 preimage preservation,
exact readback verified. No failed runtime parent. Ordinary startup untouched.

Host observer20cases, cache62cases, retention/map tests, image import/residency,
copy/allocation tests and13 diskless CPU cases passed. All CPU fixtures closed.
Host tests substitute APIs; next physical Windows boot remains unqualified.
Source preparation001 failed on a comment-only namespace assumption; fresh002
used. Observer host001 failed on stale expected status after a newer read;
host002 corrected assertion passed with unchanged observer. Failures retained.

Next stage unique E:/Applications/XWN16Boot841, readback, commit/push and one
SITE20s. After2min obtain screen. If B4 capture LOAD841 rows and XWN841 rows.
If desktop leave running. No automatic return, no hook. Then user power off/on,
authenticate dashboard and collect once. Never relaunch CLOSED runs. Old
automation paused; direct user Windows desktop work remains active.
'''
(K/'NEXT.md').write_text(note)
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:p.write_bytes(note.encode()+b'\n'+p.read_bytes())
print('841 exact inputs frozen; no launch requested')
