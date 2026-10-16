"""Read-only instruction/string-reference classification; not binary equivalence."""
import hashlib
import json
import re
import sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'))
import capstone
from compare import pe


def strings(data,layout,address):
    rva=address-layout['image_base']
    matches=[s for s in layout['sections'] if s['rva']<=rva<s['rva']+s['bytes'] and not s['characteristics']&0x20000000]
    if len(matches)!=1:return None
    s=matches[0];at=s['raw']+rva-s['rva'];raw=data[at:min(s['raw']+s['bytes'],at+512)]
    end=raw.find(b'\0')
    if end<0:return None
    raw=raw[:end]
    if not raw or any(v<32 and v not in [9,10,13] or v>126 for v in raw):return None
    return raw.decode('ascii')


def classify(a,b,base):
    pa,pb=pe(a,base),pe(b,base)
    md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);md.detail=True;md.skipdata=True
    result=[]
    for sa in pa['sections']:
        if not sa['characteristics']&0x20000000:continue
        sb=next(s for s in pb['sections'] if s['name']==sa['name'])
        assert sa==sb
        start=sa['raw'];end=start+sa['bytes'];va=pa['image_base']+sa['rva']
        old={i.address:i for i in md.disasm(a[start:end],va)}
        new={i.address:i for i in md.disasm(b[start:end],va)}
        changed={start+i for i,(x,y) in enumerate(zip(a[start:end],b[start:end])) if x!=y}
        covered=set()
        for address,ins in old.items():
            offset=start+address-va;diff={v for v in changed if offset<=v<offset+ins.size}
            if not diff:continue
            other=new.get(address)
            row=dict(section=sa['name'],address=address,file_offset=offset,differing_bytes=len(diff),
                     demo=ins.mnemonic+' '+ins.op_str,fresh=None if other is None else other.mnemonic+' '+other.op_str,
                     classification='Unclassified instruction/data difference')
            if ins.id and other and other.id and ins.size==other.size and ins.id==other.id:
                ia,ib=ins.encoding,other.encoding
                if ia.imm_size==ib.imm_size==4 and ia.imm_offset==ib.imm_offset:
                    span=set(range(offset+ia.imm_offset,offset+ia.imm_offset+4))
                    if diff<=span:
                        aa=int.from_bytes(ins.bytes[ia.imm_offset:ia.imm_offset+4],'little')
                        bb=int.from_bytes(other.bytes[ib.imm_offset:ib.imm_offset+4],'little')
                        ta,tb=strings(a,pa,aa),strings(b,pb,bb)
                        if ta is not None and tb is not None:
                            row['target_strings']=dict(demo=ta,fresh=tb)
                            row['classification']='Relocated identical string reference' if ta==tb else 'Changed string reference'
            covered|=diff;result.append(row)
        assert covered==changed,'Changed executable bytes not decoded'
    return result


if __name__=='__main__':
    result={}
    for name in ['Applications/XWNEBoot/loader/halxboxnt5.dll','Applications/XWNEBoot/freeldr.sys','Applications/XWNEBoot/rosload.exe']:
        a=(Path('E:/xwn415/demo')/name).read_bytes();b=(Path('E:/xwn415/fresh')/name).read_bytes()
        rows=classify(a,b,2048 if name.endswith('freeldr.sys') else 0)
        counts={key:sum(v['classification']==key for v in rows) for key in sorted({v['classification'] for v in rows})}
        result[name]=dict(demo_sha256=hashlib.sha256(a).hexdigest(),fresh_sha256=hashlib.sha256(b).hexdigest(),
                          classification_counts=counts,instructions=rows)
    out=dict(capstone_version=capstone.__version__,files=result,
             scope='Changed executable-section bytes only. Data, relocation tables and complete equivalence require separate review.',
             runtime_equivalence_proved=False)
    with (K/'instructions001.json').open('x',encoding='utf-8') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps({k:v['classification_counts'] for k,v in result.items()},indent=2))
