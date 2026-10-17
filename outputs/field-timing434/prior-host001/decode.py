"""Independent bounded transport decoder; raw timing observations, no parity claim."""
import statistics, struct
CR=(0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39)
MM=(0x600800,0x600804,0x680508,0x680600,0x680800,0x680804,0x680808,
    0x68080c,0x680810,0x680814,0x680818,0x680820,0x680824,0x680828,
    0x68082c,0x680830,0x680834,0x680838,0x680848,0x680880,0x680884,
    0x680888,0x68088c,0x680898,0x68089c,0x6808c0,0x6808c4,0x68084c,0x680630)
def require(v, message):
    if not v: raise ValueError(message)
def u64(words, index): return words[index] | (words[index+1]<<32)
def decode(data, stage):
    require(stage in (0,1,2), 'stage argument')
    require(1024<=len(data)<=1024+32768*24, 'size bounds')
    a=struct.unpack_from('<128I',data); b=struct.unpack_from('<128I',data,512)
    w,h=(1920,1080) if stage==1 else (1280,720)
    for r in (a,b):
        require(r[:6]==(0x434c0de,1,stage,w,h,w*4), 'identity/geometry')
        require(r[6]==r[7]==r[64] and 0<r[6]<0x4000000, 'scanout base')
        require(w*h*4<=r[8]<=0x4000000-r[6], 'allocation')
        require(1000<=u64(r,9)<=1000000000 and r[13:15]==(60,32), 'clock/mode')
        require((r[15]&255)==1, 'HDTV pack')
        require(r[16]==r[17] and ((r[18]^r[19])&0x200)==0, 'selector/interrupt restoration')
        require(r[20:22]==(len(CR),len(MM)), 'register count')
        require(all(x<=255 for x in r[32:55]), 'CRTC byte range')
        require(all(x==0 for x in r[55:64]+r[93:128]), 'reserved header')
        require(r[12]==0 and r[28:30]==(0,0) and r[31]==0, 'native failure/pixels')
    require(a[11]==0 and a[22:26]==(0,0,0,0) and a[30]==0,'initial state')
    require(a[0:11]==b[0:11] and a[13:16]==b[13:16] and a[26:28]==b[26:28], 'immutable identity')
    require(a[32:55]==b[32:55] and a[64:93]==b[64:93], 'static registers changed')
    count=b[11];freq=u64(b,9);begin=u64(b,22);end=u64(b,24)
    require(64<=count<32768 and len(data)==1024+count*24,'sample count/length')
    require(begin<end and freq//5<=end-begin<=freq and 0<b[30]<1000,'coverage/deadline')
    values=[];times=[];durations=[];last=begin
    for i,(pre,raw,post,seq) in enumerate(struct.iter_unpack('<QIQI',data[1024:])):
        require(seq==i and last<=pre<=post<=end,'sequence/timestamps')
        values.append(raw);times.append(pre);durations.append(post-pre);last=post
    drops=[i for i in range(1,count) if values[i]<values[i-1]]
    intervals=[(times[j]-times[i])*1000/freq for i,j in zip(drops,drops[1:])]
    differences=[(times[i]-times[i-1])*1000000/freq for i in range(1,count)]
    active=0
    for raw in values: active |= raw^values[0]
    return dict(collection_passed=True,stage=stage,width=w,height=h,samples=count,
        frequency=freq,elapsed_ms=(end-begin)*1000/freq,wall_ms=b[30],
        physical=hex(a[6]),allocation=a[8],kernel_build=a[26],kernel_qfe=a[27],
        crtc={hex(i):v for i,v in zip(CR,a[32:55])},
        mmio={hex(i):v for i,v in zip(MM,a[64:93])},
        raw_min=min(values),raw_max=max(values),raw_unique=len(set(values)),
        varying_bits=hex(active),raw_decreases=len(drops),
        decrease_interval_ms=intervals,
        sample_gap_us=dict(min=min(differences),median=statistics.median(differences),max=max(differences)),
        read_bracket_us_max=max(durations)*1000000/freq,
        field_parity_proved=False,signal_or_visual_qualification=False,
        interpretation='Unmasked raw raster observations. Decreases are not independently attested field boundaries.')
def terminal(data):
    require(len(data)==64,'terminal length')
    a,b=struct.unpack('<8I',data[:32]),struct.unpack('<8I',data[32:])
    require(a==(0x434c0de,1,99,0,0,0,0,0),'initial record')
    require(b==(0x434c0de,1,100,0,3,0,0,0),'terminal record')
