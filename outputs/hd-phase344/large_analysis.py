"""Strict327 extension parser. Legacy206 and cold/run gates must pass separately."""
SIZES=((256,128),(640,360),(960,540))
KINDS=('fill','ram_upload','overlap_down_right','overlap_up_left','wm_paint')

def analyze(log):
    result={'passed':False,'scope':'327 extension only; legacy/runtime/cold checks remain separate'}
    try:
        if not isinstance(log,str) or len(log)>4*1024*1024:raise ValueError('log bound/type')
        words=[v.split() for v in log.splitlines()]
        if not words or any(len(v)!=4 for v in words):raise ValueError('row shape')
        if words[-1]!=['PASS','0','0','0']:raise ValueError('overall terminal absent')
        if any(v[0].startswith(('FAIL','MISMATCH','CANCELLED')) for v in words):raise ValueError('failure marker')
        rows=[]
        for v in words:
            if v[0].startswith('LARGE_'):
                if any(not n.isascii() or not n.isdecimal() for n in v[1:]):raise ValueError('non-unsigned integer')
                nums=tuple(map(int,v[1:]))
                if any(n>0xffffffff for n in nums):raise ValueError('integer overflow')
                rows.append((v[0],*nums))
        pos=0
        def take(tag):
            nonlocal pos
            if pos>=len(rows) or rows[pos][0]!=tag:raise ValueError('missing/extra/out-of-order '+tag)
            v=rows[pos][1:];pos+=1;return v
        def exact(tag,*expected):
            if take(tag)!=expected:raise ValueError('incorrect '+tag)
        def packet(ident,phase):
            exact('LARGE_STATS_CALL',ident,phase,1)
            values=[]
            for index in range(32):
                row=take('LARGE_STATS_AFTER' if phase else 'LARGE_STATS_BEFORE')
                if row[:2]!=(ident,index):raise ValueError('packet index/identity')
                values.append(row[2])
            if values[:2]!=[0x53525758,112] or values[19:21]!=[0,1] or values[21:]!=[0]*11:raise ValueError('packet contract')
            if any(v==0xffffffff for v in values[2:17]):raise ValueError('saturated counter')
            return values
        exact('LARGE_VERSION',327,3,5);cases=[]
        for size,(w,h) in enumerate(SIZES):
            cw,ch=w+48,h+48
            exact('LARGE_SIZE',size,w,h);exact('LARGE_LAYOUT',size,cw*4,cw*ch*4);exact('LARGE_CLIENT',size,cw,ch)
            for kind in range(5):
                ident=size*5+kind
                exact('LARGE_PIXEL_CHECK',ident,cw*ch,1)
                before=packet(ident,0)
                who,count,ms=take('LARGE_TIMING')
                if who!=ident or not 1<=count<=20000 or not 750<=ms<=30000:raise ValueError('timing/count bound')
                exact('LARGE_PAINTS',ident,count if kind==4 else 0,0)
                after=packet(ident,1)
                if any(a<b for a,b in zip(after[2:17],before[2:17])):raise ValueError('counter regression')
                uploads=after[16]-before[16]
                amount=after[17]+(after[18]<<32)-before[17]-(before[18]<<32)
                if uploads<count or amount<w*h*4*count:raise ValueError('insufficient copy coverage')
                exact('LARGE_UPLOADS',ident,uploads,0)
                exact('LARGE_BYTES',ident,amount&0xffffffff,amount>>32)
                exact('LARGE_PIXEL_CHECK',ident,cw*ch,1);exact('LARGE_CASE_PASS',ident,1,0)
                cases.append(dict(size=[w,h],kind=KINDS[kind],operations=count,elapsed_ms=ms,
                                  operations_per_second=count*1000/ms,global_uploads=uploads,
                                  global_copied_bytes=amount,minimum_workload_bytes=w*h*4*count))
        exact('LARGE_COMPLETE',3,15,0)
        if pos!=len(rows):raise ValueError('trailing extension rows')
        result.update(passed=True,cases=cases,limits='Device-global counters may include background work. Timings include flush, dispatch and visibility checks; exclude readback, pixel validation and statistics snapshots. Not display FPS.')
    except (ValueError,TypeError,IndexError) as exc:result['error']=str(exc)
    return result
