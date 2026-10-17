"""Independent complete pattern oracle; captured CPU pixels, not emitted fields."""
import struct
CR=(0,1,2,3,4,5,6,7,9,0x10,0x11,0x12,0x13,0x15,0x16,0x17,0x18,0x19,0x1a,0x25,0x28,0x2d,0x39)
MM=(0x600800,0x600804,0x680508,0x680600,0x680800,0x680804,0x680808,
    0x68080c,0x680810,0x680814,0x680818,0x680820,0x680824,0x680828,
    0x68082c,0x680830,0x680834,0x680838,0x680848,0x680880,0x680884,
    0x680888,0x68088c,0x680898,0x68089c,0x6808c0,0x6808c4,0x68084c,0x680630)

def require(v,msg):
    if not v: raise ValueError(msg)

def expected(phase):
    rows=[]
    for y in range(512):
        row=y+(phase%2)
        colors=[0xffffff if row%2 else 0]*320
        colors += [0xffffff if (row//2)%2 else 0]*320
        for bit in range(10): colors += [0xffffff if row&(1<<bit) else 0]*32
        colors += [0x00ff00 if row%2 else 0xff00ff]*64
        rows.append(struct.pack('<1024I',*colors))
    return b''.join(rows)

def decode(data,phase):
    require(phase in range(4),'phase argument')
    require(len(data)==512+1024*512*4,'length')
    r=struct.unpack_from('<128I',data)
    require(r[:6]==(0x435c0de,1,phase,1920,1080,7680),'identity/mode')
    require(0<r[6]<0x4000000 and r[6]==r[7]==r[64],'scanout')
    require(8294400<=r[8]<=0x4000000-r[6],'allocation')
    require(r[9]==r[6]+0x80000000,'pointer identity')
    require(r[10]>0 and r[11:15]==(0,0,60,32),'native status')
    require((r[15]&255)==4,'HDTV pack')
    require(r[16]==r[17] and not ((r[18]^r[19])&512),'selector/interrupt')
    require(r[20:22]==(23,29),'register counts')
    require(r[23]==int(phase>=2),'initialization identity')
    if phase>=2:
        require(r[10]>=12288,'memory guard')
        require(r[24:27]==(1920,1080,7680) and 0<r[27]<0x4000000,'PBKit buffer identity')
        require(not (r[6]<=r[27]<r[6]+r[8]),'PBKit/debug alias')
    else: require(r[24:28]==(0,0,0,0),'premature PBKit state')
    require(r[28:30]==(0,0) and r[31]==0,'native pixel/reserved')
    require(all(v<256 for v in r[32:55]),'CRTC range')
    require(not any(r[55:64]+r[93:128]),'reserved')
    cr=dict(zip(CR,r[32:55]));mm=dict(zip(MM,r[64:93]))
    require((cr[0x13]+((cr[0x19]&224)<<3))*8==7680,'actual CRTC pitch')
    require(mm[0x680800]==1079,'output height')
    require(data[512:]==expected(phase),'independent pixel oracle')
    return dict(phase=phase,pixels=524288,physical=r[6],pointer=r[9],allocation=r[8],
        available_pages_before_init=r[10],pbkit_back_physical=r[27],
        crtc={hex(k):v for k,v in cr.items()},mmio={hex(k):v for k,v in mm.items()},
        signal_qualified=False)

def terminal(data):
    require(len(data)==8*64,'journal length')
    rows=list(struct.iter_unpack('<16I',data))
    require([r[2] for r in rows]==[99,10,11,20,21,12,13,100],'journal sequence')
    require([r[4] for r in rows]==[0,1,2,2,2,3,4,4],'completed phases')
    require([r[5] for r in rows]==[0,0,0,0,0,1,1,0],'init/API results')
    for r in rows:
        require(r[:2]==(0x435c0de,1) and r[3]==0 and not any(r[13:]),'journal error/reserved')
    require(rows[3][6]>=12288,'fresh memory guard')
    for r in rows[1:]:
        require(r[7:10]==rows[1][7:10],'journal allocation identity')
    return dict(records=8,error=0,phases=4,init_return=rows[4][5],free_pages=rows[3][6])

def paired(modes):
    require(len(modes)==4,'complete phases')
    require([m['phase'] for m in modes]==list(range(4)),'phase order')
    for m in modes:
        require(all(m[k]==modes[0][k] for k in ('physical','pointer','allocation')),'same framebuffer')
    return {kind:{key:[modes[0][kind][key],modes[2][kind][key]]
        for key in modes[0][kind] if modes[0][kind][key]!=modes[2][kind][key]}
        for kind in ('crtc','mmio')}
