"""Decode NT5 x86 CM_RESOURCE_LIST/IO_RESOURCE_REQUIREMENTS_LIST; retain raw pins."""
import hashlib,json,struct
from pathlib import Path
k=Path(__file__).resolve().parent
p=k/'physical189-resources.json';source=json.loads(p.read_text());rows=[]
for key,values in source['phases']['after'].items():
    if not key.endswith('\\LogConf'):continue
    row={'key':key,'values':{}}
    for name,value in values.items():
        data=bytes.fromhex(value['hex']);items=[]
        if name=='BootConfig':
            assert value['type']==8
            count,interface,bus=struct.unpack_from('<III',data)
            assert count==1
            version,revision,n=struct.unpack_from('<HHI',data,12)
            assert len(data)==20+n*16
            for i in range(n):
                off=20+16*i;typ,share,flags=struct.unpack_from('<BBH',data,off)
                item={'type':typ,'share':share,'flags':flags,'raw':data[off:off+16].hex()}
                if typ in (1,3): item.update(start=struct.unpack_from('<Q',data,off+4)[0],length=struct.unpack_from('<I',data,off+12)[0])
                items.append(item)
            decoded={'interface_type':interface,'bus':bus,'version':version,'revision':revision,'descriptors':items}
        elif name=='BasicConfigVector':
            assert value['type']==10
            size,interface,bus,slot=struct.unpack_from('<4I',data)
            alternatives=struct.unpack_from('<I',data,28)[0]
            assert size==len(data) and alternatives==1
            version,revision,n=struct.unpack_from('<HHI',data,32)
            assert len(data)==40+n*32
            for i in range(n):
                off=40+i*32;option,typ,share,_,flags=struct.unpack_from('<BBBBH',data,off)
                item={'option':option,'type':typ,'share':share,'flags':flags,'raw':data[off:off+32].hex()}
                if typ in (1,3):
                    length,align,low,high=struct.unpack_from('<IIQQ',data,off+8)
                    item.update(length=length,alignment=align,minimum=low,maximum=high)
                if typ in (2,0x81):item['data']=list(struct.unpack_from('<III',data,off+8))
                items.append(item)
            decoded={'interface_type':interface,'bus':bus,'slot_number':slot,'version':version,'revision':revision,'descriptors':items}
        else:continue
        row['values'][name]=decoded
    rows.append(row)
report={'scope':__doc__,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'devices':rows,
        'limits':'Registry requirements/boot resources, not current allocation or proof of codec presence. x86 layouts only; fail closed on unexpected lengths/types.'}
dest=k/'physical189-resource-decode.json';assert not dest.exists();dest.write_text(json.dumps(report,indent=2)+'\n')
for row in rows:
    print(row['key'])
    print(json.dumps({name:[{key:value for key,value in d.items() if key!='raw'} for d in desc['descriptors']] for name,desc in row['values'].items()},indent=2))
