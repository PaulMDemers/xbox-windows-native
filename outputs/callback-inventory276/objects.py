"""Pinned pbkit object classes, creation order and actual descriptor ranges."""
import struct,hashlib
DMA_ORDER=[3,5,4,9,10,11,2,7,12,8,6]
CLASSES={2:3,3:0x3d,4:3,5:2,6:2,7:0x3d,8:0x3d,9:0x3d,10:0x3d,11:0x3d,12:0x3d,13:0x97,14:0x39,16:0x9f,17:0x62}

def commands(data):
    assert 0<len(data)<=4*1024**2 and len(data)%4==0
    words=struct.unpack('<'+'I'*(len(data)//4),data);i=0;events=[];a=b=None
    while i<len(words):
        word=words[i];i+=1
        assert word&0xa0030003==0,'Unsupported jump/call or reserved packet bits'
        count=(word>>18)&2047;method=word&0x1ffc;channel=(word>>13)&7
        assert count>0 and i+count<=len(words)
        for j,value in enumerate(words[i:i+count]):
            m=method+(0 if word&0x40000000 else j*4)
            if channel==0:
                if m==0x1d8c:a=value
                if m==0x1d90:b=value
                if m==0x1a8:events.append(dict(kind='interrupt_context_binding',handle=value))
                if m==0x100:events.append(dict(kind='interrupt',code=value,parameter_a=a,parameter_b=b))
        i+=count
    assert any(e['kind']=='interrupt_context_binding' and e['handle']==12 for e in events)
    assert any(e['kind']=='interrupt' and e['code']==0xb2a and e['parameter_a'] is not None and e['parameter_b'] is not None for e in events)
    return dict(packet_words=len(words),special_context_events=events,scope='Retained owned pushbuffer packets, not a trace of every executed instruction')
def inspect(ramht,pb,h,read):
    assert len(ramht)==4096 and pb['_pb_FifoChannelID']==0
    rows=[];seen=set();ranges=[];big=pb['_pb_GrCtxInst'];free=pb['_pb_FreeInst']
    expected={handle:big-11+i for i,handle in enumerate(DMA_ORDER)}
    expected.update({13:big+0x37f,14:big+0x37f+0x33,16:big+0x37f+0x34,17:big+0x37f+0x35})
    assert free==expected[17]+1
    for slot in range(512):
        handle,context=struct.unpack_from('<II',ramht,slot*8)
        if not(handle or context):continue
        assert handle in CLASSES and handle not in seen;seen.add(handle)
        index=(((handle>>11)^handle)>>11)^handle;assert index==slot
        graphics=handle>=13;instance=context&0xffff
        assert context==(0x80000000|(int(graphics)<<16)|expected[handle]) and instance==expected[handle]
        size=0x330 if handle==13 else 16
        assert 0x1000<=instance and instance*16+size<=free*16<=0x20000
        assert instance*16+size<=big*16 or instance>=big+0x37f
        for a,n in ranges:assert instance*16+size<=a or a+n<=instance*16
        ranges.append((instance*16,size))
        data=read(0xfd700000+(instance<<4),size,'object-'+str(handle))
        assert len(data)==size
        words=struct.unpack_from('<4I',data)
        if graphics:
            assert words[0]==CLASSES[handle]|(0x01000000 if handle==14 else 0),('Graphics class',handle,words)
            # Full bytes retained. Mutable graphics state is not assumed zero.
            classification='Owned pbkit graphics instance, full bounded descriptor captured; class and instance range checked'
        else:
            base,limit,flags=0,0x03ffafff,0xb000|CLASSES[handle]
            if handle in [2,7,8]:
                base=pb['_pb_DmaBuffer'+str(handle)]&0x03ffffff
                limit=0x20 if handle==8 else 0x1f;flags|=0x20000
            elif handle in [9,11]:base=h[28];limit=h[29]*h[30]-1
            elif handle==10:base=pb['_pb_DSAddr']&0x03ffffff;limit=pb['_pb_DepthStencilPitch']*h[30]-1
            elif handle==12:limit=0x10000000;flags|=0x20000
            assert words==(flags,limit,base|3,base|3),('DMA descriptor',handle,words,(flags,limit,base|3,base|3))
            if handle==12:
                classification='Owned pbkit interrupt-trigger context; NOT a RAM range or native Windows grant'
            else:
                assert base+limit+1<=0x03ffb000
                classification='Owned pbkit DMA descriptor; broad common RAM contexts are not exclusive allocation grants'
        rows.append(dict(handle=handle,instance=instance,graphics=graphics,class_id=CLASSES[handle],bytes=size,sha256=hashlib.sha256(data).hexdigest(),words=list(words),classification=classification))
    assert seen==set(CLASSES)
    return dict(count=15,objects=rows,full_descriptors_captured=True,native_windows_gpu_grant=False,
        scope='RAMHT channel/hash/creation order, classes and bounded instance ranges; exact DMA fields. Graphics mutable state retained, not all bits semantically decoded.')
