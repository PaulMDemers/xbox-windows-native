"""Exact CPU baseline grammar; no renderer/pixel preservation inference."""
def analyze(raw):
    assert isinstance(raw,bytes) and len(raw)<4096 and raw.endswith(b'\r\n')
    rows=[line.split() for line in raw.decode('ascii').splitlines()]
    assert len(rows)==6 and all(len(v)==4 for v in rows)
    assert rows[0][0]=='ALLOCATED_CPU_ONLY'
    gen,physical,size=map(int,rows[0][1:]);assert gen==1 and size==16384
    assert not physical&4095 and 0x100000<=physical<=0x03bfc000
    for i in range(3):assert rows[i+1]==['EXACT_CPU_BYTES',str(i),'16384','0']
    assert rows[4]==['CPU_COUNTS','3','2','0']
    assert rows[5]==['COMPLETE_CPU_ONLY','49152','1','0']
    return dict(passed=True,generation=gen,physical=physical,allocation_bytes=size,
                verified_bytes=49152,reads=3,writes=2,quarantine_reported=True,
                renderer_references=False,pixel_preservation_proved=False)
