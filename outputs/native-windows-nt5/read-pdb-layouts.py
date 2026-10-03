"""Read selected C structure layouts from the exact Microsoft PDB 2.0.

MSF2 container layout reference: moyix/pdbparse PDB2RootStream.
CodeView record definitions: microsoft/microsoft-pdb/include/cvinfo.h.
Supports only the explicit record forms needed here; rejects unknown fields.
"""
import hashlib,json,pathlib,struct
r=pathlib.Path(__file__).resolve().parents[2]
p=(r/'work/symbols/ntoskrnl-2195-7376.pdb').read_bytes()
sig=b'Microsoft C/C++ program database 2.00\r\n\x1aJG\0\0'
fmt=f'<{len(sig)}sIHHII';magic,block,free,npages,rootlen,res=struct.unpack_from(fmt,p)
assert magic==sig and npages*block==len(p)
def page_data(pages,size):return b''.join(p[n*block:(n+1)*block] for n in pages)[:size]
pages=struct.unpack_from('<'+'H'*((rootlen+block-1)//block),p,struct.calcsize(fmt))
directory=page_data(pages,rootlen);n,res=struct.unpack_from('<HH',directory)
sizes=[struct.unpack_from('<II',directory,4+8*i)[0] for i in range(n)]
off=4+8*n;streams=[]
for size in sizes:
    if size==0xffffffff:size=0
    count=(size+block-1)//block
    pages=struct.unpack_from('<'+'H'*count,directory,off);off+=count*2
    streams.append(page_data(pages,size))
tpi=streams[2];version,header,first,last,length=struct.unpack_from('<5I',tpi)
assert header+length==len(tpi)
types={};pos=header
for index in range(first,last):
    size=struct.unpack_from('<H',tpi,pos)[0];pos+=2
    types[index]=tpi[pos:pos+size];pos+=size
assert pos==len(tpi)
def numeric(data,pos):
    n=struct.unpack_from('<H',data,pos)[0];pos+=2
    if n<0x8000:return n,pos
    formats={0x8000:'b',0x8001:'h',0x8002:'H',0x8003:'i',0x8004:'I',0x8009:'q',0x800a:'Q'}
    fmt=formats[n];return struct.unpack_from('<'+fmt,data,pos)[0],pos+struct.calcsize(fmt)
def string(data,pos):
    size=data[pos];return data[pos+1:pos+1+size].decode('ascii'),pos+1+size
structs={}
for index,data in types.items():
    leaf=struct.unpack_from('<H',data)[0]
    if leaf not in (0x1004,0x1005):continue
    leaf,count,props,fields,derived,vshape=struct.unpack_from('<HHHIII',data)
    size,end=numeric(data,18);name,end=string(data,end)
    if not props&0x80:structs[name]={'type_index':index,'size':size,'field_count':count,'field_list':fields}
def fields(index,seen=None):
    seen=set() if seen is None else seen
    assert index not in seen;seen.add(index)
    data=types[index];assert struct.unpack_from('<H',data)[0]==0x1203
    result={};pos=2
    while pos<len(data):
        if data[pos]>=0xf0:
            skip=data[pos]&15;assert skip;pos+=skip;continue
        leaf=struct.unpack_from('<H',data,pos)[0]
        if leaf==0x1404:
            nxt=struct.unpack_from('<I',data,pos+4)[0];pos+=8
            result.update(fields(nxt,seen));continue
        assert leaf==0x1405,(hex(index),hex(leaf),pos)
        attr,typ=struct.unpack_from('<HI',data,pos+2)
        offset,end=numeric(data,pos+8);name,pos=string(data,end)
        result[name]={'offset':offset,'type_index':typ}
    return result
selected={}
for name in ('_KPCR','_KPRCB','_KTHREAD','_KTRAP_FRAME','_FAST_MUTEX','_DISPATCHER_HEADER'):
    item=structs[name].copy();item['fields']=fields(item['field_list'])
    assert len(item['fields'])==item['field_count']
    selected[name]=item
report={'kernel':'5.00.2195.7376 from supplied OEM-channel ISO','pdb_sha256':hashlib.sha256(p).hexdigest(),
        'tpi_version':version,'type_count':last-first,'structures':selected,
        'references':['https://github.com/moyix/pdbparse/blob/master/pdbparse/__init__.py','https://github.com/microsoft/microsoft-pdb/blob/master/include/cvinfo.h']}
(r/'outputs/native-windows-nt5/microsoft-kernel-layouts.json').write_text(json.dumps(report,indent=2)+'\n')
for name,item in selected.items():print(name,hex(item['size']),{n:hex(f['offset']) for n,f in item['fields'].items() if n in ('Prcb','PrcbData','CurrentThread','BuildType','MajorVersion','DebugActive','Header','Eip','EFlags','ExceptionList','OldIrql','Count','Event','Owner','Contention')})
