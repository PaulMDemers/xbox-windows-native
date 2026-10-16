import hashlib,json,struct
from pathlib import Path
from decode import decode
K=Path(__file__).resolve().parent;P=Path('E:/xwn409/host002')
out=K/'decoder001.json';assert not out.exists()
accepted=[];rejected=0
def refuse(b):
    global rejected
    try:decode(b)
    except ValueError:rejected+=1;return
    raise AssertionError('Accepted malformed report')
for i in range(13):
    b=(P/f'case{i:02d}.bin').read_bytes()
    if i in (0,1,2,3,4,9,12):
        decode(b);accepted.append(i)
    else:refuse(b)
b=(P/'case00.bin').read_bytes()
for n in range(80):refuse(b[:n])
refuse(b+b'\0')
for at in [0,4,8,12,20,48,60,64,68,72,76]:
    for value in [0,0xffffffff,0x12345678]:
        c=bytearray(b);struct.pack_into('<I',c,at,value)
        if c!=b:refuse(c)
for at,value in [(24,0),(28,0),(28,0x400001),(28,0x2000000),(32,0),(36,0),(40,0xc0000017),(44,0),(52,0x400),(56,0)]:
    c=bytearray(b);struct.pack_into('<I',c,at,value);refuse(c)
files=[K/'decode.py',K/'test-decode.py',K/'test-wrapper002.c',P/'test-wrapper',P/'result.log']+sorted(P.glob('case*.bin'))
r=dict(passed=True,actual_x86_host_cases=13,complete_modeled_reports_accepted=accepted,negative_controls_rejected=rejected,
       final_flush_failure_not_inferable_from_report_alone=True,physical_access=False,
       files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
out.write_text(json.dumps(r,indent=2)+'\n');print(r['negative_controls_rejected'])
