"""Freeze source/binary/host dependencies before the single physical comparison."""
import hashlib,json,re,struct
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn435/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'review002.json';assert not out.exists()
b=json.loads((K/'build001.json').read_text());assert b['compiled'] and b['sdk_unchanged']
for n,r in b['outputs'].items():assert sha(P/n)==r['sha256']
for n,h in b['source'].items():assert sha(K/n)==sha(P/'input'/n)==h
for n,h in b['sdk_after'].items():assert sha(Path('C:/nxdk')/n)==h
assert json.loads((K/'host001.json').read_text())['negative_cases']==203
assert (K/'pattern.h').read_bytes()==(W/'outputs/stock-field430/pattern.h').read_bytes().replace(b'\r\n',b'\n')
s=(K/'main.c').read_text()
assert not re.search(r'VIDEOREG\([^\n]+\)\s*=',s)
assert 'HalWriteSMBusValue' not in s and 'pb_finished(' not in s and 'pb_kill(' not in s
assert s.count('pb_init()')==1 and s.count('pb_show_debug_screen()')==1
assert 'freepages<48u*1024u*1024u/4096u' in s and 'GetTickCount()-start)<10000' in s
assert s.index('error=phase(1)')<s.index('init=pb_init()')<s.index('error=phase(2)')
mp=(P/'main.map').read_text()
for name in ['_pb_init ', '_pb_busy ', '_pb_show_debug_screen ', '_pb_shutdown_notification_routine ',
             '_automount_d_drive ', '__imp__MmQueryStatistics@4','__imp__HalReturnToFirmware@4']:
    assert name in mp,name
exe=(P/'main.exe').read_bytes();pe=struct.unpack_from('<I',exe,0x3c)[0]
assert exe[:2]==b'MZ' and exe[pe:pe+4]==b'PE\0\0'
assert struct.unpack_from('<H',exe,pe+4)[0]==0x14c
assert struct.unpack_from('<I',exe,pe+24+56)[0]<2*1024**2
assert b'D:\\result.dat\0' in exe and b'D:\\phase-0.dat\0' in exe
assert (P/'bin/default.xbe').read_bytes()[:4]==b'XBEH'
pb=Path('C:/nxdk/lib/pbkit/pbkit.c').read_text()
assert 'pb_shutdown_registration.NotificationRoutine = pb_shutdown_notification_routine;' in pb
assert 'VIDEOREG(PCRTC_START)=((DWORD)XVideoGetFB())&0x0FFFFFFF;' in pb
assert 'NV_PCRTC_CONFIG_START_ADDRESS_HSYNC' in pb
paths=[K/n for n in ['main.c','pattern.h','decode.py','test_decode.py','host001.json','physical.py',
    'DESIGN.md','build001.json','review.py']]
paths += [P/n for n in ['main.exe','main.map','bin/default.xbe','disassembly.txt']]
paths += [W/n for n in ['outputs/field-scanout428/physical.py','outputs/demo-audio-level256/common001.py',
 'outputs/surface-bridge260/atomic_json.py','tools/configure-e-display.py',
 'tools/e-display-policy.json','outputs/demo-integration399/accepted-state.json']]
paths += [Path('C:/nxdk')/n for n in ['lib/pbkit/pbkit.c','lib/pbkit/pbkit.h','lib/pbkit/outer.h',
 'lib/libpbkit.lib','lib/hal/video.c','lib/hal/video.h','lib/xboxkrnl/xboxkrnl.h',
 'lib/nxdk/automount_d.c','lib/winapi/fileio.c']]
r=dict(passed=True,xbe_sha256=sha(P/'bin/default.xbe'),files={str(p):sha(p) for p in paths},
 pattern_difference='CRLF to LF only; native input remains frozen',sdk_unchanged=True,host_negatives=203,physical_launched=False,
 scope='Broad normal PBKit init with same stock framebuffer via supported debug-screen API',
 exclusions=['No direct timing/encoder patch','No Windows/driver changes','No full GPU ownership claim',
             'No emitted-field or visual result yet','No bounded SDK-call cancellation guarantee'])
out.write_text(json.dumps(r,indent=2)+'\n');print({k:r[k] for k in ('passed','xbe_sha256','host_negatives')})
