import hashlib,json,struct
from pathlib import Path
from decode import decode
K=Path(__file__).resolve().parent;P=Path('E:/xwn462/host001')
out=K/'decoder001.json';assert not out.exists()
accepted=[];rejected=0

def refuse(b):
    global rejected
    try:decode(b)
    except ValueError:rejected+=1;return
    raise AssertionError('Accepted malformed report')

for i in range(45):
    b=(P/f'case{i:02d}.bin').read_bytes()
    if i in (5,6,7,8,10,11,*range(21,32)):refuse(b)
    else:
        result=decode(b);accepted.append(i)
        assert result['preparation_verified']==(i in (0,9,12,*range(32,44)))
b=(P/'case00.bin').read_bytes()
for n in range(176):refuse(b[:n])
refuse(b+b'\0')
for at in [0,4,8,12,20,48,60,64,68,72,76,80,108,116,120,124,128,132,144,148,152,156,160,164,168,172]:
    for value in [0,0xffffffff,0x12345678]:
        c=bytearray(b);struct.pack_into('<I',c,at,value)
        if c!=b:refuse(c)
for at in [96,100,104]:
    c=bytearray(b);struct.pack_into('<I',c,at,0)
    struct.pack_into('<I',c,124,0)
    assert not decode(c)['preparation_verified']
    for value in [2,0xffffffff]:
        struct.pack_into('<I',c,at,value);refuse(c)
for at,value in [(120,0),(124,0),(128,0),(132,0),(144,0),(148,0),(152,0),(156,0),(24,0),(28,0),(32,0),(36,0),(40,0xc0000017),(44,0),(52,0x400),(56,0),(84,0x4000000),(84,1),(88,0),(92,0)]:
    c=bytearray(b);struct.pack_into('<I',c,at,value);refuse(c)
files=[K/'decode.py',K/'test-decode.py',K/'test-wrapper.c',P/'test-wrapper',P/'host.log']+sorted(P.glob('case*.bin'))
r=dict(passed=True,actual_x86_host_cases=45,complete_reports_accepted=accepted,negative_controls_rejected=rejected,
       final_flush_close_and_postlog_refusals_not_inferable_from_report_alone=True,physical_access=False,
       files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
out.write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8');print(json.dumps({x:r[x] for x in ['passed','actual_x86_host_cases','negative_controls_rejected']}))
