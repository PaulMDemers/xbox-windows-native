"""Freeze a qualified isolated diagnostic837 before physical staging."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];A=W/'outputs/boot720-root836'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert read(A/'closed001.json')['state']=='CLOSED'
records=['source002','baseline001','driver002','driver-host002','driver-review001','qualify001','chain002','host006','cpu-build010','cpu-run010','build001']
for n in records[2:]:assert read(K/(n+'.json'))['passed']
assert read(K/'cpu-run010.json')['closed']
pins={p.name:sha(p) for p in K.iterdir() if p.is_file() and (p.suffix in ['.py','.c','.h','.S','.ld','.patch'] or p.name in ['Makefile','.gitattributes']+[n+'.json' for n in records])}
out=K/'launch-source-pins001.json';assert not out.exists();out.write_text(json.dumps(pins,indent=2)+'\n')
note='''# Fresh837 isolated cache diagnostic qualified; next stage and one boot

836 CLOSED after user power off/on, authenticated dashboard, one preparation
collection and cold audit. Ten critical installed files unchanged, no new root
files or changed retained logs. Windows kernel STOP0A at MmMapViewInSystemCache+fb;
readable fixed720p blue screen, no desktop. Never relaunch/recollect836.

837 uses the same retained720p handoff and FATX loader root fix, with new owned
boot paths. It loads diagnostic xwnfatx from its private loader folder for this
boot only; installed driver and registry remain untouched. Exact baseline driver
source8e12297c;42 cache call sites wrapped. Requests beyond page-rounded FileSize
stop E8370001(site,offsetLow,length,sizeLow); null FsContext E8370003. This is a
diagnostic stop, not a filesystem repair. Recent4 ring records print at bugcheck
via resident callback, with site/offsetHi/Lo/length/sizeHi/Lo/flags. Registration
failure E8370002. Valid requests forward unchanged. Caller/offset remain unknown
until physical evidence. Root-sizing lead is not established crash cause.

Driver001 link failed on missing NTAPI HalDisplayString declaration; retained.
Source002 supplies declaration, driver002 PASS. Actual diagnostic62 host cases,
NT5 kernel/HAL imports and nonpageable residency passed. Fresh boot chain002,
retention/map/page/allocation and13 diskless CPU contexts passed; all VMs closed.
Pins launch-source-pins001.json. No host runtime or hook. Stage create-only unique
E:/Applications/XWN16Boot837, read back every file, then ONE SITE20s bound. No
launch retry. After2min request screen. If held, photograph then power off/on,
authenticate dashboard and collect837 once. Ordinary startup/protected720p intact.
Old automation paused; direct user Windows desktop work continues.
'''
(K/'NEXT.md').write_text(note)
(A/'NEXT.md').write_text('# Boot836 CLOSED: Windows kernel STOP0A\n\nSee closed001.json and audit001.json. Never relaunch/recollect.\nNext: ../boot720-cache837/NEXT.md\n')
for p in [W/'outputs/engineering-notes/CONTINUATION.md',W/'outputs/engineering-notes/STATUS.md',W/'docs/current-status.md']:p.write_bytes(note.encode()+b'\n'+p.read_bytes())
print('837 launch sources frozen; no hardware launch requested')
