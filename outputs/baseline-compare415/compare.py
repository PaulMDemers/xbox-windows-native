"""Classify exact live-demo versus clean-build bytes; never infer runtime success."""
import hashlib
import json
import struct
from pathlib import Path

K=Path(__file__).resolve().parent
W=K.parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()


def pe(data,base=0):
    assert data[base:base+2]==b'MZ'
    p=base+struct.unpack_from('<I',data,base+60)[0]
    assert data[p:p+4]==b'PE\0\0'
    count=struct.unpack_from('<H',data,p+6)[0]
    optional=p+24
    n=struct.unpack_from('<H',data,p+20)[0]
    assert struct.unpack_from('<H',data,optional)[0]==0x10b and 0<count<40
    sections=[]
    for i in range(count):
        at=optional+n+40*i
        name=data[at:at+8].rstrip(b'\0').decode('ascii')
        vs,rva,size,raw=struct.unpack_from('<IIII',data,at+8)
        assert base+raw+size<=len(data)
        sections.append(dict(name=name,rva=rva,virtual_size=vs,bytes=size,raw=base+raw,
                             characteristics=struct.unpack_from('<I',data,at+36)[0]))
    def offset(rva):
        matches=[s for s in sections if s['rva']<=rva<s['rva']+s['bytes']]
        assert len(matches)==1
        s=matches[0]
        return s['raw']+rva-s['rva']
    fields={'coff_timestamp':(p+8,4),'checksum':(optional+64,4)}
    exports=struct.unpack_from('<I',data,optional+96)[0]
    if exports:
        fields['export_timestamp']=(offset(exports)+4,4)
    return dict(base=base,image_base=struct.unpack_from('<I',data,optional+28)[0],
                entry_rva=struct.unpack_from('<I',data,optional+16)[0],sections=sections,fields=fields)


def pe_compare(a,b,base=0):
    pa,pb=pe(a,base),pe(b,base)
    changed=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    same_layout=pa==pb
    allowed={i for o,n in pa['fields'].values() for i in range(o,o+n)} if same_layout else set()
    metadata_only=len(a)==len(b) and same_layout and set(changed)<=allowed
    return dict(kind='PE',bytes=[len(a),len(b)],different_bytes=len(changed)+abs(len(a)-len(b)),
                same_layout=same_layout,timestamp_checksum_only=metadata_only,
                differing_sections=[dict(name=s['name'],changed_bytes=sum(s['raw']<=i<s['raw']+s['bytes'] for i in changed),
                                         executable=bool(s['characteristics']&0x20000000)) for s in pa['sections']
                                    if any(s['raw']<=i<s['raw']+s['bytes'] for i in changed)],
                metadata_fields={k:dict(offset=o,bytes=n,demo=a[o:o+n].hex(),fresh=b[o:o+n].hex()) for k,(o,n) in pa['fields'].items()},
                scope='Byte classification only; nonmetadata differences require review')


def xbe_compare(a,b):
    assert a[:4]==b[:4]==b'XBEH' and len(a)==len(b)
    base=struct.unpack_from('<I',a,0x104)[0]
    count,table=struct.unpack_from('<II',a,0x11c)
    assert (base,count,table)==(struct.unpack_from('<I',b,0x104)[0],*struct.unpack_from('<II',b,0x11c))
    assert 0<count<=8
    digest_offsets=set()
    for i in range(count):
        s=table-base+i*56
        off,size=struct.unpack_from('<II',a,s+12)
        assert (off,size)==struct.unpack_from('<II',b,s+12) and off+size<=len(a)
        for data in [a,b]:
            assert hashlib.sha1(struct.pack('<I',size)+data[off:off+size]).digest()==data[s+36:s+56]
        digest_offsets.update(range(s+36,s+56))
    date_a=b'Oct 13 2026 (rev. %s)'
    date_b=b'Oct 14 2026 (rev. %s)'
    assert a.count(date_a)==b.count(date_b)==1
    pos=a.index(date_a)
    assert pos==b.index(date_b)
    allowed=digest_offsets|set(range(pos,pos+len(date_a)))
    changed={i for i,(x,y) in enumerate(zip(a,b)) if x!=y}
    assert changed<=allowed
    # The section mapping was independently pinned against the original ELF in413.
    assert a[0x1100:0x3000]==b[0x1100:0x3000]
    assert a[0x3000:0x3000+0x3434c]==b[0x3000:0x3000+0x3434c]
    return dict(kind='XBE',different_bytes=len(changed),wrapper_and_cromwell_text_exact=True,
                only_display_date_and_valid_section_digest=True,date_offset=pos,
                display_dates=['Oct 13 2026','Oct 14 2026'],runtime_equivalence_claim=False)


if __name__=='__main__':
    demo=json.loads((K/'physical001.json').read_text(encoding='utf-8'))
    fresh=json.loads((K/'fresh001.json').read_text(encoding='utf-8'))
    rows=[]
    for path,record in demo['files'].items():
        key=path[3:].lower()
        other=fresh['files'].get(key)
        if not other:
            rows.append(dict(path=key,classification='Absent from fresh installation'))
            continue
        a=(Path('E:/xwn415/demo')/path[3:]).read_bytes()
        b=Path(other['local_path'].replace('/mnt/e/','E:/')).read_bytes()
        assert sha(a)==record['sha256'] and sha(b)==other['sha256']
        row=dict(path=key,demo_sha256=sha(a),fresh_sha256=sha(b))
        if a==b:row['classification']='Byte-identical'
        elif key.endswith('.xbe'):row.update(classification='Display date and section digest only',details=xbe_compare(a,b))
        elif a[:2]==b'MZ' or key.endswith('/freeldr.sys'):
            details=pe_compare(a,b,2048 if key.endswith('/freeldr.sys') else 0)
            row.update(classification='PE timestamps/checksum only' if details['timestamp_checksum_only'] else 'Nonmetadata binary differences',details=details)
        else:row.update(classification='Configuration/state difference',bytes=[len(a),len(b)])
        rows.append(row)
    result=dict(physical_writes=False,launch_requested=False,comparison=rows,
                no_same_build_same_route_intermittency_established=True,
                clean_rebuild_not_deployed_over_physical_demo=True,
                scope='Selected current files compared with audited406 clean installation; not full installation equivalence')
    with (K/'comparison001.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps([(v['path'],v['classification']) for v in rows],indent=2))
