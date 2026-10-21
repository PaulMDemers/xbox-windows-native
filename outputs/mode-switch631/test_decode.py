"""Synthetic protocol controls, explicitly not physical display evidence."""
import json,zlib
from pathlib import Path
from decode import decode,CR,MM,MODES
from oracle import oracle

lines=['XWN_HD631 version=1 kernel=1.0.4034.1','SETTINGS value=004f0104']
expected=[]
for stage,(w,h) in enumerate(MODES,1):
    crc=zlib.crc32(oracle(w,h));n=w*h*4
    expected.append(dict(stage=stage,width=w,height=h,bytes=n,crc=f'{crc:08x}'))
    lines += [f'SET stage={stage} width={w} height={h} tick=100',
        f'MODE stage={stage} width={w} height={h} bytes={n} allocation={(n+4095)&~4095} physical=00100000 scanout=00100000 hvalid={w-1} vvalid={h-1} mismatches=0 crc={crc:08x} tick=200']
    lines += [f'FP stage={stage} index={i} value={(h-1 if i==6 else w-1 if i==14 else 0):08x}' for i in range(16)]
    lines += [f'TIMING stage={stage} index_before=40 index_after=40 flags_before=00000202 flags_after=00000246']
    values={0x13:(w*4//8)&255,0x19:((w*4//8)>>8)<<5,0x28:0x83,0x39:255}
    lines += [f'CRTC stage={stage} index={i:02x} value={values.get(i,0):02x}' for i in CR]
    lines += [f'MMIO stage={stage} offset={i:08x} value=00000000' for i in MM]
    lines += [f'GEOMETRY stage={stage} pitch={w*4} format=3 interlace=ff']
lines += ['COMPLETE error=0 log_ok=1 mode_changes=3']
blob=('\r\n'.join(lines)+'\r\n').encode('ascii')
assert decode(blob)['passed']
bad=[]
for i in range(len(lines)):
    bad.append(('missing row '+str(i),'\r\n'.join(lines[:i]+lines[i+1:]).encode()))
    bad.append(('duplicate row '+str(i),'\r\n'.join(lines[:i]+[lines[i]]+lines[i:]).encode()))
for old,new in [('settings','unused'),('004f0104','004f0101'),('004f0104','00400104'),
    ('scanout=00100000','scanout=00101000'),('hvalid=719','hvalid=639'),('vvalid=479','vvalid=480'),
    ('mismatches=0','mismatches=1'),('allocation=1384448','allocation=4096'),
    ('index_after=40','index_after=41'),('flags_after=00000246','flags_after=00000046'),
    ('index=13 value=68','index=13 value=40'),('index=39 value=ff','index=39 value=10'),
    ('format=3','format=2'),('pitch=2880','pitch=2560'),('log_ok=1','log_ok=0'),
    ('error=0','error=6'),('mode_changes=3','mode_changes=2')]:
    if old=='settings':continue
    assert old.encode() in blob,old
    bad.append((old,blob.replace(old.encode(),new.encode(),1)))
bad += [('trailing junk',blob+b'junk\r\n'),('bad ASCII',blob+b'\xff')]
for label,data in bad:
    try:decode(data)
    except (AssertionError,ValueError,UnicodeError):pass
    else:raise AssertionError('Accepted '+label)
k=Path(__file__).resolve().parent
for name,data in [('expected.json',expected),('decoder-tests001.json',dict(passed=True,positive=1,negative=len(bad),scope='synthetic decoder/oracle only; no guest or physical run'))]:
    p=k/name;assert not p.exists();p.write_text(json.dumps(data,indent=2)+'\n')
print('Decoder accepted one synthetic sequence and rejected',len(bad),'malformed sequences')
