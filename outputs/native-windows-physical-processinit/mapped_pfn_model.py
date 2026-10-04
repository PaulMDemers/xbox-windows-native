import struct,hashlib

def permission_mask(read,k,pte):
    u32=lambda a:struct.unpack('<I',read(k+a,4))[0]
    if pte<=u32(0x82270):return 5
    if 0xc0300000<=pte<0xc0303000:return 5 if pte<=u32(0x823a4) else 1
    return u32(0x73df0)|1

def snapshot(read,k):
    u32=lambda a:struct.unpack('<I',read(a,4))[0]
    directory=list(struct.unpack('<1024I',read(0xc0300000,4096)))
    tables={}
    for i,pde in enumerate(directory):
        if not pde&1:continue
        assert not pde&0x80
        tables[pde>>12]=list(struct.unpack('<1024I',read(0xc0000000+i*4096,4096)))
    return {'directory':directory,'tables':tables,'globals':{off:u32(k+off) for off in [0x73df0,0x82270,0x823a4,0x823dc,0x81c9c,0x823e0,0x81bb4]},
        'pfn':b''.join(read(0xffb85000+i*4096,4096) for i in range(91))}

def expected(s):
    g=s['globals'];assert g[0x823e0]==0 and g[0x81bb4]==0x3bff
    tables={p:list(v) for p,v in s['tables'].items()};directory=tables[s['directory'][768]>>12]
    assert directory==s['directory']
    data=bytearray(91*4096)
    for i in range(64):struct.pack_into('<I',data,90*4096+i*8,0xffffffff)
    def u32(o):return struct.unpack_from('<I',data,o)[0]
    def w32(o,v):struct.pack_into('<I',data,o,v&0xffffffff)
    def init(pfn,pte,parent):
        assert pfn<=0x3bff
        o=pfn*24;w32(o+8,u32(o+8)+1);w32(o+4,pte);w32(o+20,parent)
        w32(o+12,((u32(o+12)|0x10000)&0xfffffe8f)|0x600)
    def mask(pte):
        if pte<=g[0x82270]:return 5
        if 0xc0300000<=pte<0xc0303000:return 5 if pte<=g[0x823a4] else 1
        return g[0x73df0]|1
    pde_count=pte_count=entry_updates=0
    for i in range(1024):
        pde=directory[i]
        if not pde&1:continue
        assert not pde&0x80
        frame=pde>>12;pte_base=0xc0000000+i*4096
        init(frame,0xc0300000+i*4,directory[768]>>12);pde_count+=1
        directory[i]|=mask(pte_base)
        for j in range(1024):
            value=tables[frame][j]
            if not value&1:continue
            va=(i<<22)|(j<<12);pte=pte_base+j*4
            tables[frame][j]|=mask(pte);pte_count+=1
            w32(frame*24+8,u32(frame*24+8)+1)
            if value>>12<=0x3bff and va>=0xa0000000:
                init(value>>12,pte,frame);entry_updates+=1
    return data,tables,{'pde_count':pde_count,'present_pte_count':pte_count,'mapped_pfn_updates':entry_updates,
        'populated_pfn_records':sum(bool(u32(i*24+12)>>16) for i in range(0x3c00)),
        'color_heads':64,'pfn_sha256':hashlib.sha256(data).hexdigest()}

def verify(before,after):
    data,tables,report=expected(before)
    assert after['pfn']==data,[(hex(i),hex(a),hex(b)) for i,(a,b) in enumerate(zip(after['pfn'],data)) if a!=b][:25]
    assert after['tables'].keys()==tables.keys()
    for pfn,values in tables.items():
        assert all((a&~0x60)==(b&~0x60) for a,b in zip(values,after['tables'][pfn])),hex(pfn)
    report['all_pfn_bytes_match_model']=True;report['all_paging_entries_match_model']=True
    return report
