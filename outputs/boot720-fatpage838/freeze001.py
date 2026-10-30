"""Freeze qualified838 sources; isolated driver, ordinary retained720p boot."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-cache837'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(A/'closed001.json')['state']=='CLOSED'
records=['source001','baseline001','fatpage002','driver002','driver-host002','driver-review001','qualify001','chain002','host006','cpu-build010','cpu-run010','build001']
for n in records[2:]:assert read(K/(n+'.json'))['passed']
assert read(K/'cpu-run010.json')['closed']
assert read(K/'source001.json')['retention_unchanged_sha256']==read(A/'source002.json')['retention_unchanged_sha256']
assert read(K/'source001.json')['loader_fat_unchanged_sha256']==read(A/'source002.json')['loader_fat_unchanged_sha256']
pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.c','.h','.S','.ld','.patch'] or p.name in ['Makefile','.gitattributes']+[n+'.json' for n in records])}
out=K/'launch-source-pins001.json';assert not out.exists();out.write_text(json.dumps(pins,indent=2)+'\n')
note='''# Fresh838 qualified: FATX metadata page-window repair; next stage and boot

837 CLOSED. Photo E8370001(1D,130000,4000,132000) identifies a FAT32
free-space count request8KiB beyond the FAT stream allocation/file size. Its
cache guard stopped before forwarding; no desktop. Dashboard authenticated,
one collection/cold audit complete; ten installed critical files unchanged.
Never relaunch/recollect/runtime-parent837. Source-only reuse has exact pins.

838 changes FATX16/32 table get/count/allocate/write windows to PAGE_SIZE because
table length rounds to4KiB independently of16KiB data clusters. Standard FAT
policy unchanged. Diagnostic838 still checks extent and prints recent cache
requests; no gate waiver. Loader only overrides xwnfatx from the owned838 folder;
installed driver/hives/ordinary startup untouched. Retained720p and loader root
fix source bytes unchanged. This is not a root-directory driver repair.

Actual previous C reproduces the exact physical overrun; corrected eight routines
pass1429 cases/4434 bounded maps under ASan/UBSan. This substitutes cache APIs,
not NT-cache or persistence validation. Source preparation001 encoding failure
and host harness001 extraction failure retained. Fresh source002 and harness002
PASS. Driver imports/residency and62 diagnostic cases PASS; chain, retention,
memory/alias checks and13 diskless CPU fixtures PASS, all VMs closed.

Next stage unique E:/Applications/XWN16Boot838; readback all9 files and baseline,
then ONE SITE20s bound. No hook. No host runtime. After2min request screen. If held,
capture evidence then power off/on; authenticate dashboard and collect838 once.
If desktop, leave running. Old automation paused; direct user desktop work active.
'''
(K/'NEXT.md').write_text(note)
(A/'NEXT.md').write_text('# Boot837 CLOSED: FAT metadata map overrun\n\nSee screen001.json, fault-analysis001.json, collection001.json, audit001.json, closed001.json.\nNo relaunch/recollection. Next: ../boot720-fatpage838/NEXT.md\n')
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:p.write_bytes(note.encode()+b'\n'+p.read_bytes())
print('838 exact launch inputs frozen; no launch requested')
