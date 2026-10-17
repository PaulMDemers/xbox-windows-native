"""Prelaunch source, actual build output, SDK, header and host decoder review."""
import hashlib,json,re,struct
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn434/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'review002.json';assert not out.exists()
b=json.loads((K/'build001.json').read_text());assert b['compiled'] and b['sdk_unchanged']
for n,r in b['outputs'].items():assert sha(P/n)==r['sha256']
for n,h in b['source'].items():assert sha(K/n)==sha(P/'input'/n)==h
for n,h in b['sdk_after'].items():assert sha(Path('C:/nxdk')/n)==h
host=json.loads((K/'host002.json').read_text());assert host['passed'] and host['negative_cases']==79
assert '#define AV_PACK_HDTV 0x00000004' in Path('C:/nxdk/lib/xboxkrnl/xboxkrnl.h').read_text()
assert (K/'pattern.h').read_bytes()==(W/'outputs/stock-field430/pattern.h').read_bytes()
s=(K/'main.c').read_text()
assert s.count('VIDEOREG(0x600808)')==1
assert not re.search(r'VIDEOREG\([^\n]+\)\s*=',s)
assert not re.search(r'(?:^|[;{])\s*\*data\s*=',s) and 'HalWriteSMBusValue' not in s
assert 'end-begin<freq/5' in s and 'count<CAPACITY' in s and 'GetTickCount()-tick)<1000' in s
assert 'KeStallExecutionProcessor(10)' in s and 'CREATE_NEW' in s
dis=(P/'disassembly.txt').read_text()
assert '8b 35 08 08 60 fd' in dis and '1162c:' in dis
assert dis.count('8b 35 08 08 60 fd')==1
assert dis.count('\tcli')>=2 and dis.count('\tpopfd')>=2
mp=(P/'main.map').read_text()
for name in ['_automount_d_drive','__imp__KeQueryPerformanceCounter@0',
             '__imp__KeQueryPerformanceFrequency@0','__imp__KeStallExecutionProcessor@4',
             '__imp__AvSetDisplayMode@24','__imp__HalReturnToFirmware@4']:
    assert name in mp,name
exe=(P/'main.exe').read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0]
assert exe[:2]==b'MZ' and exe[pe:pe+4]==b'PE\0\0'
assert struct.unpack_from('<H',exe,pe+4)[0]==0x14c
assert struct.unpack_from('<I',exe,pe+24+56)[0]<2*1024**2
xbe=(P/'bin/default.xbe').read_bytes();assert xbe[:4]==b'XBEH'
assert b'D:\\result.dat\0' in exe and b'D:\\raster-0.dat\0' in exe
paths=[K/n for n in ['main.c','pattern.h','decode.py','test_decode.py','host002.json',
                     'physical.py','DESIGN.md','build001.json','review.py']]
paths += [P/n for n in ['main.exe','main.map','bin/default.xbe','disassembly.txt']]
paths += [W/n for n in ['outputs/field-scanout428/physical.py',
 'outputs/demo-audio-level256/common001.py','outputs/surface-bridge260/atomic_json.py',
 'tools/configure-e-display.py','tools/e-display-policy.json',
 'outputs/demo-integration399/accepted-state.json']]
paths += [Path('C:/nxdk')/n for n in ['lib/hal/video.c','lib/hal/video.h',
 'lib/xboxkrnl/xboxkrnl.h','lib/nxdk/automount_d.c','lib/winapi/fileio.c']]
r=dict(passed=True,xbe_sha256=sha(P/'bin/default.xbe'),files={str(p):sha(p) for p in paths},
       host_negative_cases=79,sdk_unchanged=True,physical_launched=False,
       raster_load_instruction='0x1162c: mov esi,dword ptr [0xfd600808], bracketed by imported kernel counter calls',
       direct_register_write_scope='Only saved/restored CRTC index; no timing/encoder/IRQ-enable/GPU writes',
       path_scope='D is Xbox CRT launch-directory alias, not a host drive or Xbox system partition',
       host001_limitation='Synthetic model used wrong HDTV pack enum 1; source review caught it before launch. Original retained, corrected host002 uses actual nxdk enum 4.',
       limits=['Stock synchronous mode/file calls have no individual cancellation guarantee',
               'Raw raster counter does not prove framebuffer fetch parity or external signal',
               'Native pixel check uses same helper; not an independent full framebuffer capture',
               'No emulator timing claim; upstream raster implementation is a stub'])
out.write_text(json.dumps(r,indent=2)+'\n');print({n:r[n] for n in ['passed','xbe_sha256','host_negative_cases']})
