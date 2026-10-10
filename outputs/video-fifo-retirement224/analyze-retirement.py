"""Strict observation grammar and independent raw-word reason reconstruction; never a GPU grant."""
OFFSETS=[0x3200,0x3204,0x3210,0x3214,0x3220,0x3228,0x324c,0x3240,0x3244,0x3250,0x3270,0x2400,0x2100,0x400100,0x400144,0x400148]
REASONS={1:'DMA_DATA',2:'METHOD',4:'SUBROUTINE',8:'CACHE',16:'RUNOUT',32:'GRAPH_IRQ',64:'DMA_ERROR',128:'FIFO_IRQ',256:'CHANGED',512:'DMA_SUSPENDED',0x40000000:'UNMODELED_BUSY',0x80000000:'NO_OWNERSHIP'}
def decode(words):
    reasons=0xc0000000
    for v in words:
        if v[7]!=v[8]:reasons|=1
        if v[5]&0x1ffc0000:reasons|=2
        if v[6]&1:reasons|=4
        if not v[3]&0x10 or v[2]!=v[10]:reasons|=8
        if not v[11]&0x10:reasons|=16
        if v[13]:reasons|=32
        if v[5]&0xe0000000:reasons|=64
        if v[12]:reasons|=128
        if v[4]&0x1000:reasons|=512
        if v!=words[0]:reasons|=256
    return reasons
def analyze(data,enabled):
    r=dict(passed=False,gpu_ownership_qualified=False,gpu_writes=False)
    try:
        assert isinstance(data,bytes) and len(data)<16384 and data.endswith(b'\r\n')
        rows=[]
        for line in data.decode('ascii').splitlines():
            p=line.split();assert len(p)==4;v=[int(x) for x in p[1:]];assert all(0<=x<=0xffffffff for x in v);rows.append((p[0],v))
        # OWNER=2, STALE=3 are the unchanged222 native contract.
        assert rows[0]==('RET_OWNER',[2,0,0]) and rows[1]==('RET_STALE',[3,0,0])
        assert rows[2]==('RET_SUMMARY',[21,8,128] if enabled else [20,0,0])
        assert rows[3][0]=='RET_REASONS' and rows[3][1][1:]==[1,0]
        assert rows[-1]==('RET_COMPLETE_NO_GRANT',[224,0,0])
        middle=rows[4:-1];assert len(middle)==(128 if enabled else 0)
        words=[]
        for round in range(8 if enabled else 0):
            values=[]
            for i in range(16):
                tag,v=middle[round*16+i];assert tag=='RET_WORD' and v[:2]==[round,i];values.append(v[2])
            words.append(values)
        reasons=decode(words);assert rows[3][1][0]==reasons
        r.update(passed=True,enabled=enabled,rounds=len(words),reads=len(middle),reason_mask=reasons,
                 reason_names=[name for bit,name in REASONS.items() if reasons&bit],offsets=OFFSETS,raw_words=words,
                 lifetime_rejections_before_reads=True,short_input_rejected_before_complete=True,
                 limits='Eight immediate non-atomic sequential snapshots. Source-instrumented read counts; no debugger. Unmodeled busy/backend drain and genuine producer/instance ownership remain unresolved.')
    except (AssertionError,ValueError,UnicodeError,TypeError) as exc:r['error']=repr(exc)
    return r
